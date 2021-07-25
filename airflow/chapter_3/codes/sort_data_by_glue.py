import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.dynamicframe import DynamicFrame
from pyspark.sql.types import StringType, IntegerType
from pyspark.sql.functions import udf
from awsglue.utils import getResolvedOptions

# parameter
args = getResolvedOptions(sys.argv, ['S3_KEY'])
s3_key = args['S3_KEY']

def stripDQ(string):
    return string.replace(' ', "")
    
udf_stripDQ = udf(stripDQ, StringType())

args = getResolvedOptions(sys.argv, ['JOB_NAME'])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)
datasource0 = glueContext.create_dynamic_frame.from_catalog(database = "topic-2", table_name = "data", transformation_ctx = "datasource0")
spark_df = datasource0.toDF()

for column in spark_df.columns:
    if "gender" != column:
        spark_df = spark_df.withColumn(column, udf_stripDQ(spark_df[column]))
        spark_df = spark_df.withColumn(column,spark_df[column].cast(IntegerType()))
    else:
        spark_df = spark_df.withColumn(column,spark_df[column].cast(StringType()))

spark_df= spark_df.sort("spending score (1-100)")
spark_df.coalesce(1).write.mode('overwrite').option("header", "true").csv(s3_key)
job.commit()