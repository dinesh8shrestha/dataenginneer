#!/usr/bin/env python3

from pyspark.sql import SparkSession
from pyspark.streaming import StreamingContext
from pyspark.sql import functions as F
from pyspark.sql.types import *

from pyspark.sql.functions import explode
from pyspark.sql.functions import split

from pyspark.sql.functions import from_json


topic_in = "name_surname"
topic_out = topic_in+"_lab02_out"
kafka_bootstrap = "10.132.0.2:6667"
checkpoint_read = "/tmp/checkpoint-read"
checkpoint_write= "/tmp/checkpoint-write"
agg_window = "600 seconds"

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

st = spark \
  .readStream \
  .format("kafka") \
  .option("checkpointLocation", checkpoint_read)\
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
  .groupby(F.window(st.timestamp, agg_window))\
  .agg(
    F.sum(F.when(F.col("eventType")=="itemBuyEvent",F.col("item_price")).otherwise(0)).alias("revenue"),
    F.approx_count_distinct(F.when(F.col("eventType")=="itemBuyEvent", F.col("partyId")).otherwise(None)).alias("buyers"),
    F.approx_count_distinct(F.col("partyId")).alias("visitors"),
    F.approx_count_distinct(F.when(F.col("eventType")=="itemBuyEvent", F.col("sessionId")).otherwise(None)).alias("purchases")
  )\
  .withColumn("aov", F.col("revenue")/F.col("purchases"))\

out_columns=["start_ts", "end_ts", "revenue", "visitors", "purchases", "aov"]

query = out_df.select("window.*",
                      "revenue", "visitors", "purchases", "aov")\
              .select(F.col("start").cast("long").alias("start_ts"),
                      F.col("end").cast("long").alias("end_ts"),
                      "revenue", "visitors", "purchases", "aov")\
              .select(F.to_json(F.struct(*out_columns)).alias("value"))\
    .writeStream \
    .outputMode("update")\
    .format("kafka") \
    .option("checkpointLocation", checkpoint_write)\
    .option("kafka.bootstrap.servers", kafka_bootstrap ) \
    .option("topic", topic_out) \
    .start()

query.awaitTermination()