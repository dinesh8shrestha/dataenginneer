#!/usr/bin/env python3

from pyspark.sql import SparkSession
from pyspark.streaming import StreamingContext
from pyspark.sql import functions as F
from pyspark.sql.types import *

from pyspark.sql.functions import explode
from pyspark.sql.functions import split

from pyspark.sql.functions import from_json


topic_in = "artem.trunov"
topic_out = "out."+topic_in
kafka_bootstrap = "34.76.77.30:6667"

spark = SparkSession.builder.appName("SimpleStreamingApp").getOrCreate()
spark.sparkContext.setLogLevel('WARN')


schema = StructType(
   fields = [
      StructField("timestamp", LongType(), True),
      StructField("referer", StringType(), True),
      StructField("location", StringType(), True),
      StructField("remoteHost", StringType(), True),
      StructField("partyId", StringType(), True),
      StructField("sessionId", StringType(), True),
      StructField("pageViewId", StringType(), True),
      StructField("eventType", StringType(), True),
      StructField("item_id", StringType(), True),
      StructField("item_price",IntegerType(), True),
      StructField("item_url", StringType(), True),
      StructField("basket_price",StringType(), True),
      StructField("detectedDuplicate", BooleanType(), True),
      StructField("detectedCorruption", BooleanType(), True),
      StructField("firstInSession", BooleanType(), True),
      StructField("userAgentName", StringType(), True),
])

#newJson = '{"timestamp": 1540817494, "referer": "https://b24-d2wt09.bitrix24.shop/katalog/item/dress-spring-ease/", "location": "https://b24-d2wt09.bitrix24.shop/", "remoteHost": "test0", "partyId": "0:jmz8xo3z:BvkQdVYMXSAUTS42oNOW8Yg7kSdkkdHl", "sessionId": "0:jnu6ph44:kxtaa4hPKImjpoyQSgSYCuzoFOMrHA4f", "pageViewId": "0:PvFIq25Zl1esub4LGUQ75xAuoYH0XAlj", "eventType": "itemViewEvent", "item_id": "bx_40480796_7_52eccb44ded0bb34f72b273e9a62ef02", "item_price": "2331", "item_url": "https://b24-d2wt09.bitrix24.shop/katalog/item/t-shirt-mens-purity/", "basket_price": "", "detectedDuplicate": false, "detectedCorruption": false, "firstInSession": true, "userAgentName": "TEST_UserAgentName"}'


st = spark \
  .readStream \
  .format("kafka") \
  .option("checkpointLocation", "file:///tmp/checkpoint")\
  .option("kafka.bootstrap.servers", kafka_bootstrap ) \
  .option("subscribe", topic_in) \
  .option("startingOffsets", "latest") \
  .load() \
  .selectExpr("CAST(value as string)")\
  .select(from_json("value", schema).alias("value"))\
  .select(F.col("value.*"))\
  .filter(~ F.col("detectedDuplicate"))\
  .filter(~ F.col("detectedCorruption"))\
  .withColumn("timestamp", F.col("timestamp")/1000)\
  .select(F.col("timestamp").cast("timestamp"), "eventType", F.col("item_price").cast("integer"), "partyId", "sessionId")


out_df = st\
  .groupby(F.window(st.timestamp, "600 seconds"))\
  .agg(
    F.sum(F.when(F.col("eventType")=="itemBuyEvent",F.col("item_price")).otherwise(0)).alias("revenue"),
    F.approx_count_distinct(F.when(F.col("eventType")=="itemBuyEvent", F.col("partyId")).otherwise(None)).alias("buyers"),
    F.approx_count_distinct(F.col("partyId")).alias("visitors"),
    F.approx_count_distinct(F.when(F.col("eventType")=="itemBuyEvent", F.col("sessionId")).otherwise(None)).alias("purchases")
  )\
  .withColumn("cr", F.col("buyers")/F.col("visitors"))\
  .withColumn("aov", F.col("revenue")/F.col("purchases"))\

out_columns=["start_ts", "end_ts", "revenue", "visitors", "purchases", "cr", "aov"]

query = out_df.select("window.*",
                      "revenue", "visitors", "purchases", "cr", "aov")\
              .select(F.col("start").cast("long").alias("start_ts"),
                      F.col("end").cast("long").alias("end_ts"),
                      "revenue", "visitors", "purchases", "cr", "aov")\
              .select(F.to_json(F.struct(*out_columns)).alias("value"))\
    .writeStream \
    .outputMode("complete")\
    .format("kafka") \
    .option("checkpointLocation", "file:///tmp/checkpoint")\
    .option("kafka.bootstrap.servers", kafka_bootstrap ) \
    .option("topic", topic_out) \
    .start()

query.awaitTermination()