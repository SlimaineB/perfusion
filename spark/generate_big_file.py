from pyspark.sql import SparkSession
import random

bucket_name = "perf-test"

# Configuration de Spark pour accéder à MinIO
spark = SparkSession.builder \
    .appName("MinIO S3 Write Example") \
    .config("spark.hadoop.fs.s3a.endpoint", "http://localhost:9000") \
    .config("spark.hadoop.fs.s3a.access.key", "minioadmin") \
    .config("spark.hadoop.fs.s3a.secret.key", "minioadmin") \
    .config("spark.hadoop.fs.s3a.path.style.access", "true") \
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
    .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
    .config("spark.hadoop.fs.s3a.committer.magic.enabled", "true") \
    .config("spark.hadoop.mapreduce.outputcommitter.factory.scheme.s3a", "org.apache.hadoop.fs.s3a.commit.S3ACommitterFactory") \
    .config("fs.s3a.committer.name", "magic") \
    .config("spark.sql.sources.commitProtocolClass", "org.apache.spark.internal.io.cloud.PathOutputCommitProtocol") \
    .config("spark.sql.parquet.output.committer.class", "org.apache.spark.internal.io.cloud.BindingParquetOutputCommitter") \
    .getOrCreate()

# Créer un DataFrame d'exemple
num_records = 1000000  # Nombre d'enregistrements
#num_records = 10000  # Nombre d'enregistrements
data = [(f"Name_{i}", random.randint(20, 60)) for i in range(num_records)]
columns = ["Name", "Age"]
df = spark.createDataFrame(data, columns)

# Écrire le DataFrame dans un bucket MinIO en format CSV
df.write.mode("overwrite").csv(f"s3a://{bucket_name}/input-data", header=True)

print("Data written to MinIO successfully.")

# Fermer la session Spark
spark.stop()
