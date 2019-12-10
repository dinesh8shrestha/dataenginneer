#!/home/ubuntu/dsenv/bin/python3
#
# Lab04 - Define and train a Machine Learning model
#
 
from pyspark.sql import SparkSession

import pyspark.sql.functions as F
from pyspark.sql.types import *
from pyspark.sql.functions import udf

from pyspark.ml import Pipeline
from pyspark.ml.classification import LogisticRegression
from pyspark.ml.feature import CountVectorizer
from pyspark.ml.feature import StringIndexer, IndexToString

#
# User defined variables
#
train_path = 'train_merged_labels.json'
model_path = "model.ml" 

#
# Spark init
#
spark = SparkSession.builder.appName("SimpleStreamingApp").getOrCreate()
spark.sparkContext.setLogLevel('WARN')

#
# Train dataset JSON schema
#
schema = StructType(
   fields = [
      StructField("uid", StringType(), True),
      StructField("gender_age", StringType(), True),
      StructField("visits",  ArrayType( 
          StructType(
           fields = [
            StructField("timestamp", LongType(), True),
            StructField("url", StringType(), True),

      ])), True),
])

# Read the data
train = spark.read.json(train_path, schema = schema)

print("Original data:")
train.show(5)

# Merge gender and age columns to a single column for 10 class classification
#train1 = train.withColumn("label_string", F.concat(F.col('gender'), F.lit(':'), F.col('age') ))
#print("Gender + age merged:")
#train1.show(5)

# Extract urls only from visits
train2 = train.select("uid", F.col("visits").url.alias("urls"), "gender_age")
print("URLS extracted from visits:")
train2.show(5)

#
# Helpers to extract domain names from URLs
#
import re
from urllib.parse import urlparse
from urllib.request import urlretrieve, unquote
def url2domain(url):
    url = re.sub('(http(s)*://)+', 'http://', url)
    parsed_url = urlparse(unquote(url.strip()))
    if parsed_url.scheme not in ['http','https']: return None
    netloc = re.search("(?:www\.)?(.*)", parsed_url.netloc).group(1)
    if netloc is not None: return str(netloc.encode('utf8')).strip()
    return None

# in Slack 2.4+ there is a native transform function.
# but in 2.3.1 we better use UDF
# https://stackoverflow.com/questions/48993439/typeerror-column-is-not-iterable-how-to-iterate-over-arraytype 
def transform(f, t=StringType()):
    if not isinstance(t, DataType):
       raise TypeError("Invalid type {}".format(type(t)))
    @udf(ArrayType(t))
    def _(xs):
        if xs is not None:
            return [f(x) for x in xs]
    return _

foo_udf = transform(url2domain)

# Extract domains
print("Domains extracted")
train2url = train2.withColumn('domains', foo_udf(F.col('urls')))
train2url.show(5, truncate=True)

#
# Model Definition
#
cv = CountVectorizer(inputCol="domains", outputCol="features")

lr = LogisticRegression()

indexer = StringIndexer(inputCol="gender_age", outputCol="label")

pipeline = Pipeline(stages=[cv, indexer, lr])

#
# Train the model
#
model = pipeline.fit(train2url)

#
# Save the model
#
model.write().overwrite().save(model_path)
