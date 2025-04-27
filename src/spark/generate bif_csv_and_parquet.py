from pyspark.sql import SparkSession
import os

# Initialize Spark session
spark = SparkSession.builder \
    .appName("Generate CSV and Parquet") \
    .getOrCreate()

# Generate a large DataFrame with sample data
data = [(i, f"name_{i}", i * 10) for i in range(1, 1000001)]  # 1 million rows
columns = ["id", "name", "value"]
df = spark.createDataFrame(data, columns)

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

# Write DataFrame to CSV on MinIO
csv_path = f"s3a://{bucket_name}/input/data.csv"
df.write.mode("overwrite").csv(csv_path, header=True)

# Write DataFrame to Parquet on MinIO
parquet_path = f"s3a://{bucket_name}/input/data.parquet"
df.write.mode("overwrite").parquet(parquet_path)

print(f"CSV and Parquet files written to {minio_endpoint}/{bucket_name}/input")

# Stop Spark session
spark.stop()