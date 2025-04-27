from pyspark.sql import SparkSession

# Configuration de Spark avec MinIO
spark = SparkSession.builder \
    .appName("PySpark MinIO Example") \
    .config("spark.hadoop.fs.s3a.endpoint", "http://localhost:9000") \
    .config("spark.hadoop.fs.s3a.access.key", "admin") \
    .config("spark.hadoop.fs.s3a.secret.key", "password") \
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
    .config("spark.hadoop.fs.s3a.path.style.access", "true") \
    .getOrCreate()

# Lecture d'un fichier CSV depuis MinIO
#df = spark.read.csv("s3a://mon-bucket/data.csv", header=True, inferSchema=True)

val = [{"colonne1": "valeur1", "colonne2": "valeur2"},
      {"colonne1": "valeur3", "colonne2": "valeur4"}]

# Création d'un DataFrame à partir de la liste
#df = spark.createDataFrame(val)
df = spark.createDataFrame(val, schema=["colonne1", "colonne2"])

df = df.select("colonne1")

df.coalesce(10).write.mode("overwrite").parquet("s3a://mon-bucket/data_parquet")

# Affichage du contenu
df.show()

# Écriture d'un fichier transformé dans MinIO
#df.write.mode("overwrite").parquet("s3a://mon-bucket/data_parquet")

# Arrêt de la session Spark
spark.stop()
