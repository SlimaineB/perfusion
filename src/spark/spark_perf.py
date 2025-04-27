from pyspark.sql import SparkSession
from pyspark.conf import SparkConf
import time
import yaml
import pandas as pd

NUM_ITERATIONS = 5

def parse_properties(file_path):
    with open(file_path, 'r') as f:
        properties = yaml.safe_load(f)
    return properties

def generate_values(property):
    if property["type"] == "range":
        step = property.get("step", 1)  # Default step is 1 if not specified
        unit = property.get("unit", "")  # Default unit is empty string
        return [f"{i}{unit}" for i in range(property["min"], property["max"] + 1, step)]
    elif property["type"] == "list":
        return property["values"]
    else:
        raise ValueError(f"Unknown type {property['type']}")

def test_spark_configuration(config, bucket_suffix):

    bucket_name = "perf-test"

    spark_builder = SparkSession.builder \
    .appName("MinIO S3 Write Example") \
    .config("spark.hadoop.fs.s3a.endpoint", "http://localhost:9000") \
    .config("spark.hadoop.fs.s3a.access.key", "minioadmin") \
    .config("spark.hadoop.fs.s3a.secret.key", "minioadmin") \
    .config("spark.hadoop.fs.s3a.path.style.access", "true") \
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") 
    
    for key, value in config.items():
        spark_builder = spark_builder.config(key, value)
    
    spark = spark_builder.getOrCreate()

    start_time = time.time()

    for i in range(NUM_ITERATIONS):
        # Lire les données depuis S3
        df = spark.read.csv(f"s3a://{bucket_name}/input-data")

        # Faire une opération simple
        row_count = df.count()
        #row_count = 2

        # Écrire les résultats sur S3
        df.write.mode("overwrite").csv(f"s3a://{bucket_name}/output-data")

    end_time = time.time()
    duration = end_time - start_time

    spark.stop()

    return {
        "config": config,
        "duration": duration,
        "row_count": row_count
    }

def find_best_value(param_name, values, current_config, bucket_suffix, result_df_all):
    best_duration = float('inf') # Lowest value
    worst_duration = float('-inf') # Largest value
    best_value = None
    worst_value = None

    for value in values:
        config = current_config.copy()
        config[param_name] = value
        result = test_spark_configuration(config, bucket_suffix)
        print(f"Tested {param_name}={value}, Duration: {result['duration']}s")

        if result['duration'] < best_duration:
            best_duration = result['duration']
            best_value = value

        if result['duration'] > worst_duration:
            worst_duration = result['duration']
            worst_value = value    

        df2 = pd.DataFrame([[result['duration'], param_name, value, (result['duration']  - worst_duration), str(config)]], columns=['result','last_tunned_param','last_tunned_value','diff_with_worst','config'])
        result_df_all = pd.concat([df2, result_df_all])
        result_df_all.to_csv('all_result.csv', sep='|',index=False)  

    return best_value, best_duration, result_df_all

def run_tests_iteratively(properties, initial_config, bucket_suffix):
    
    result_df_best = pd.DataFrame(columns=['result','last_tunned_param','last_tunned_value','config'])
    result_df_all = pd.DataFrame(columns=['result','last_tunned_param','last_tunned_value','diff_with_worst','config'])

    current_config = initial_config.copy()
    for param_name, property in properties.items():
        values = generate_values(property)
        best_value, best_duration, result_df_all = find_best_value(param_name, values, current_config, bucket_suffix, result_df_all)
        current_config[param_name] = best_value
        print(f"Optimal {param_name}={best_value}, Duration: {best_duration}s")

        #Save best result
        df2 = pd.DataFrame([[best_duration, param_name , best_value, str(current_config) ]], columns=['result','last_tunned_param','last_tunned_value','config'])
        result_df_best = pd.concat([df2, result_df_best])
        result_df_best.to_csv('best_result.csv', sep='|',index=False)  

    return current_config


def get_default_properties():
    print(f"Getting default_properties")
    spark = SparkSession.builder \
    .appName("MinIO S3 Write Example") \
    .config("spark.hadoop.fs.s3a.endpoint", "http://localhost:9000") \
    .config("spark.hadoop.fs.s3a.access.key", "minioadmin") \
    .config("spark.hadoop.fs.s3a.secret.key", "minioadmin") \
    .config("spark.hadoop.fs.s3a.path.style.access", "true") \
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
    .getOrCreate()
    return dict(spark.sparkContext.getConf().getAll())


def get_default_property_by_key(default_properties ,key):
    print(f"Default_property of {key} is {default_properties[key]}")
    return default_properties[key]

# Lire les propriétés du fichier
properties = parse_properties("config.yaml")
print(properties)
# Configuration initiale par défaut

default_properties = get_default_properties()


#initial_config = {key: generate_values(property)[0] for key, property in properties.items()}
initial_config = {key: get_default_property_by_key(default_properties, key) for key, property in properties.items() if key in default_properties.keys()}
#initial_config = {}

# Configurer le suffixe du bucket
bucket_suffix = "-test"

# Lancer les tests de manière itérative
optimal_config = run_tests_iteratively(properties, initial_config, bucket_suffix)

# Afficher la configuration optimale
print("Configuration optimale:", optimal_config)
