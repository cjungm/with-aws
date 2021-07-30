from pyspark.sql.types import *
from pyspark.sql import functions as F
from pyspark.sql import SparkSession, DataFrame
from pyspark import SparkContext

spark = SparkSession.builder.appName("sample").config("hive.metastore.uris", "thrift://localhost:10000").enableHiveSupport().getOrCreate()

df = spark.read.csv("file:///home/hadoop/df_from_python.csv", header=True, inferSchema='false', multiLine=True, quote='"', escape='\\', sep=',', ignoreLeadingWhiteSpace='true', ignoreTrailingWhiteSpace='true', mode='PERMISSIVE', encoding="UTF-8")
columns = df.columns
new_cols = []

for col_name in columns:
    col_name = '_'.join(char for char in col_name.split(" ") if char.isalpha())
    new_cols.append(col_name)

new_df = df.toDF(*new_cols)
new_df.distinct().write.mode('overwrite').parquet("s3://cjm-oregon/champion/emr/output/df_from_pyspark")