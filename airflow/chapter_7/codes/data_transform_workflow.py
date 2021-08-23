from pyspark.sql.types import *
from pyspark.sql import functions as F
from pyspark.sql import SparkSession, DataFrame
from pyspark import SparkContext
from pyspark.sql.functions import udf

spark = SparkSession.builder.appName("data_transform_workflow").enableHiveSupport().getOrCreate()

spark_df = spark.read.csv("s3a://cjm-oregon/champion/data/Mall_Customers.csv", header=True, inferSchema='false', multiLine=True, quote='"', escape='\\', sep=',', ignoreLeadingWhiteSpace='true', ignoreTrailingWhiteSpace='true', mode='PERMISSIVE', encoding="UTF-8")
columns = spark_df.columns
new_cols = []
print(columns)
print(spark_df.dtypes)

def stripDQ(string):
    return string.replace(' ', "")

udf_stripDQ = udf(stripDQ, StringType())

for column in spark_df.columns:
    if "Gender" != column:
        spark_df = spark_df.withColumn(column, udf_stripDQ(spark_df[column]))
        spark_df = spark_df.withColumn(column,spark_df[column].cast(IntegerType()))
    else:
        spark_df = spark_df.withColumn(column,spark_df[column].cast(StringType()))

spark_df.show()
spark_df.printSchema()
new_df= spark_df.sort("Spending Score (1-100)")

for col_name in columns:
    col_name = '_'.join(char for char in col_name.split(" ") if char.isalpha())
    new_cols.append(col_name)


new_df = new_df.toDF(*new_cols)
new_df.show()
new_df.distinct().write.mode('overwrite').parquet("s3://cjm-oregon/champion/emr/output/data_transform_workflow")