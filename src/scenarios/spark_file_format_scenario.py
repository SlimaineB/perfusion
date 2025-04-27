from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, IntegerType, StringType, DoubleType

class SparkFileFormatScenario:
    def __init__(self, bucket_name="mon-bucket"):
        self.bucket_name = bucket_name

    def run(self, **params):
        spark_builder = SparkSession.builder \
            .appName("MinIO S3 Write Example") \
            .config("spark.hadoop.fs.s3a.endpoint", "http://localhost:9000") \
            .config("spark.hadoop.fs.s3a.access.key", "admin") \
            .config("spark.hadoop.fs.s3a.secret.key", "password") \
            .config("spark.hadoop.fs.s3a.path.style.access", "true") \
            .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")

        spark = spark_builder.getOrCreate()

        schema = StructType([
            StructField("id", IntegerType(), True),
            StructField("name", StringType(), True),
            StructField("value", IntegerType(), True)
        ])

        if params.get('file_format') == "csv":
            df = spark.read.option("header", "true").schema(schema).csv(f"s3a://{self.bucket_name}/input/data.csv")
        elif params.get('file_format') == "parquet":
            df = spark.read.schema(schema).parquet(f"s3a://{self.bucket_name}/input/data.parquet")
        else:
            raise ValueError("Invalid file format. Use 'csv' or 'parquet'.")

        df = df.withColumn("new_col", (df["value"].cast("double") * 2))
        agg_result = df.groupBy("name").agg({"new_col": "avg", "id": "count"})

        df1 = df.selectExpr("id as id1", "name as name1", "new_col as new_col1")
        df2 = df.selectExpr("id as id2", "name as name2", "new_col as new_col2")
        joined_df = df1.join(df2, df1["name1"] == df2["name2"])
        filtered_df = joined_df.filter(joined_df["new_col1"] > 100)

        row_count = filtered_df.count()

        if params.get('file_format') == "csv":
            filtered_df.write.mode("overwrite").csv(f"s3a://{self.bucket_name}/output/data.csv")
        elif params.get('file_format') == "parquet":
            filtered_df.write.mode("overwrite").parquet(f"s3a://{self.bucket_name}/output/data.parquet")
        else:
            raise ValueError("Invalid file format. Use 'csv' or 'parquet'.")

        spark.stop()
        return row_count