from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, IntegerType, StringType, DoubleType

class SparkFileFormatScenario:
    def __init__(self, bucket_name="mon-bucket"):
        self.bucket_name = bucket_name
        self.spark = None

    def _initialize_spark(self):
        """Initialize the Spark session."""
        self.spark = SparkSession.builder \
            .appName("MinIO S3 Write Example") \
            .config("spark.hadoop.fs.s3a.endpoint", "http://localhost:9000") \
            .config("spark.hadoop.fs.s3a.access.key", "admin") \
            .config("spark.hadoop.fs.s3a.secret.key", "password") \
            .config("spark.hadoop.fs.s3a.path.style.access", "true") \
            .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
            .getOrCreate()

    def _get_schema(self):
        """Define the schema for the input data."""
        return StructType([
            StructField("id", IntegerType(), True),
            StructField("name", StringType(), True),
            StructField("value", IntegerType(), True)
        ])

    def _read_data(self, file_format, schema):
        """Read data from S3 based on the file format."""
        input_path = f"s3a://{self.bucket_name}/input/data.{file_format}"
        if file_format == "csv":
            return self.spark.read.option("header", "true").schema(schema).csv(input_path)
        elif file_format == "parquet":
            return self.spark.read.schema(schema).parquet(input_path)
        else:
            raise ValueError("Invalid file format. Use 'csv' or 'parquet'.")

    def _write_data(self, df, file_format):
        """Write data to S3 based on the file format."""
        output_path = f"s3a://{self.bucket_name}/output/data.{file_format}"
        if file_format == "csv":
            df.write.mode("overwrite").csv(output_path)
        elif file_format == "parquet":
            df.write.mode("overwrite").parquet(output_path)
        else:
            raise ValueError("Invalid file format. Use 'csv' or 'parquet'.")

    def run(self, **params):
        """Main method to execute the scenario."""
        self._initialize_spark()
        schema = self._get_schema()

        file_format = params.get('file_format')
        if not file_format:
            raise ValueError("Parameter 'file_format' is required.")

        df = self._read_data(file_format, schema)

        # Transformations
        df = df.withColumn("new_col", (df["value"].cast("double") * 2))
        agg_result = df.groupBy("name").agg({"new_col": "avg", "id": "count"})

        # Joins and filtering
        df1 = df.selectExpr("id as id1", "name as name1", "new_col as new_col1")
        df2 = df.selectExpr("id as id2", "name as name2", "new_col as new_col2")
        joined_df = df1.join(df2, df1["name1"] == df2["name2"])
        filtered_df = joined_df.filter(joined_df["new_col1"] > 100)

        # Count rows and write output
        row_count = filtered_df.count()
        self._write_data(filtered_df, file_format)

        self.spark.stop()
        return row_count