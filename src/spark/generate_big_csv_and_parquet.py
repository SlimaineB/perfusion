from pyspark.sql import SparkSession
from pyspark.sql.functions import col
import os
from pyspark.sql.types import StructType, StructField, IntegerType, StringType, DoubleType

# Initialize Spark session
spark = SparkSession.builder \
    .appName("Generate CSV and Parquet") \
    .config("spark.executor.memory", "8g") \
    .config("spark.driver.memory", "8g") \
    .getOrCreate()

# Generate a large DataFrame with sample data
# Définir le schéma attendu
schema = StructType([
    StructField("id", IntegerType(), True),
    StructField("name", StringType(), True),
    StructField("value", IntegerType(), True)
])

data = [(i, f"name_{i}", i * 10) for i in range(1, 4000001)]  # 4 million rows
columns = ["id", "name", "value"]
df = spark.createDataFrame(data, schema=schema)

df = df.repartition(10)  # Divise le DataFrame en 10 partitions


# MinIO configuration
minio_endpoint = "http://localhost:9000"
access_key = "admin"
secret_key = "password"
bucket_name = "mon-bucket"

# Set Hadoop configurations for MinIO
hadoop_conf = spark.sparkContext._jsc.hadoopConfiguration()
hadoop_conf.set("fs.s3a.endpoint", minio_endpoint)
hadoop_conf.set("fs.s3a.access.key", access_key)
hadoop_conf.set("fs.s3a.secret.key", secret_key)
hadoop_conf.set("fs.s3a.path.style.access", "true")
hadoop_conf.set("fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")

# Configure S3A committer
hadoop_conf.set("fs.s3a.committer.staging.conflict-mode", "replace")
hadoop_conf.set("fs.s3a.committer.staging.unique-filenames", "true")
hadoop_conf.set("fs.s3a.committer.threads", "10")

# Write DataFrame to CSV on MinIO
csv_path = f"s3a://{bucket_name}/input/data.csv"
df.write.mode("overwrite").csv(csv_path, header=True)

# Write DataFrame to Parquet on MinIO
parquet_path = f"s3a://{bucket_name}/input/data.parquet"
df.write.mode("overwrite").parquet(parquet_path)

print(f"CSV and Parquet files written to {minio_endpoint}/{bucket_name}/input")

# Stop Spark session
spark.stop()