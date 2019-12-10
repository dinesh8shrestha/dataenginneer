#
# Lab04s - implementation with GridParam search with Cross Validation
#

from pyspark.sql import SparkSession

import pyspark.sql.functions as F
from pyspark.sql.types import *
from pyspark.sql.functions import udf

from pyspark.ml import Pipeline
from pyspark.ml.classification import LogisticRegression
from pyspark.ml.feature import CountVectorizer
from pyspark.ml.feature import StringIndexer, IndexToString

from pyspark.ml.evaluation import MulticlassClassificationEvaluator
from pyspark.ml.tuning import CrossValidator, ParamGridBuilder

#
# User defined
#
train_path = 'train_merged_labels.json'
model_path = "model.ml" 

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

train = spark.read.json(train_path, schema = schema)

train.show(5)

train2 = train.select("uid", F.col("visits").url.alias("urls"), "gender_age")
train2.show(5)

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

def transform(f, t=StringType()):
    if not isinstance(t, DataType):
       raise TypeError("Invalid type {}".format(type(t)))
    @udf(ArrayType(t))
    def _(xs):
        if xs is not None:
            return [f(x) for x in xs]
    return _

foo_udf = transform(url2domain)

train2url = train2.withColumn('domains', foo_udf(F.col('urls')))
train2url.show(5, truncate=True)

#
# Model Definition
#
cv = CountVectorizer(inputCol="domains", outputCol="features")

lr = LogisticRegression() #maxIter=10, regParam=0.01)

indexer = StringIndexer(inputCol="gender_age", outputCol="label")

pipeline = Pipeline(stages=[cv, indexer, lr])

#
# Hyperparameter tuning
#
paramGrid = ParamGridBuilder() \
    .addGrid(lr.elasticNetParam, [0.1, 0.5, 0.9]) \
    .addGrid(lr.maxIter, [5, 10]) \
    .addGrid(lr.regParam, [0.001, 0.01]) \
    .build()

evaluator = MulticlassClassificationEvaluator(metricName='accuracy')

crossval = CrossValidator(estimator=pipeline,
                          estimatorParamMaps=paramGrid,
                          evaluator=evaluator,
                          numFolds=3) 

#
# Train the model
#
cv_model = crossval.fit(train2url)


#
# Save the model
#
best_model = cv_model.bestModel
best_model.write().overwrite().save(model_path)

#
# Hyperparameters
#
lr_model = best_model.stages[2]

print(
    lr_model.getOrDefault(lr_model.getParam("regParam")),
    lr_model.getOrDefault(lr_model.getParam("maxIter")),
    lr_model.getOrDefault(lr_model.getParam("elasticNetParam"))
)

# This model should give 0.2534 on test.
