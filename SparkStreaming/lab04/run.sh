#!/bin/bash
#
# Run as e.g. ./run.sh lab04_train1.py
#
# dsenv should have numpy installed.
# when --master yarn, dsenv should be replicated on all nodes

echo $1
PYSPARK_PYTHON=/home/ubuntu/dsenv/bin/python3 spark-submit \
    --conf spark.streaming.batch.duration=10 \
    --master local[1] \
    --executor-memory 4G \
    --packages org.apache.spark:spark-sql-kafka-0-10_2.11:2.3.2 \
    $1
