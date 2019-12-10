#!/usr/bin/env python3

from pyspark.sql import SparkSession
from pyspark.streaming import StreamingContext
from pyspark.sql import functions as F
from pyspark.sql.types import *

spark = SparkSession.builder.appName("SimpleStreamingApp").getOrCreate()

schema = StructType(fields = [StructField("purchase", IntegerType(), True), StructField("item_url", StringType(), True)])

batch_from_kafka = spark \
  .read \
  .format("kafka") \
  .option("kafka.bootstrap.servers", "localhost:9092") \
  .option("subscribe", "test_topic") \
  .option("startingOffsets", "earliest") \
  .option("endingOffsets", "latest") \
  .load()

batch_from_kafka \
  .select(batch_from_kafka['value'].cast("String")) \
  .show(20, False)

stream_from_kafka = spark \
  .readStream \
  .format("kafka") \
  .option("kafka.bootstrap.servers", "localhost:9092") \
  .option("subscribe", "test_topic") \
  .option("startingOffsets", "earliest") \
  .load()

tmp_df = stream_from_kafka \
  .select(stream_from_kafka['value'].cast("String")) \
  .select(F.from_json('value', schema).alias('value'))

out.awaitTermination()