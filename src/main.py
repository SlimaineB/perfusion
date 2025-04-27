import random
import optuna
import numpy as np
import os
import time
import psutil
import sys
import yaml
from pyspark.sql import SparkSession
from pyspark.conf import SparkConf

from optimizer.hyperopt_optimizer import HyperoptOptimizer
from optimizer.optuna_optimizer import OptunaOptimizer
from optimizer.allcombination_optimizer import AllCombinationOptimizer


def test_spark_file_format_configuration(**kwargs):

    bucket_name = "mon-bucket"

    spark_builder = SparkSession.builder \
    .appName("MinIO S3 Write Example") \
    .config("spark.hadoop.fs.s3a.endpoint", "http://localhost:9000") \
    .config("spark.hadoop.fs.s3a.access.key", "admin") \
    .config("spark.hadoop.fs.s3a.secret.key", "password") \
    .config("spark.hadoop.fs.s3a.path.style.access", "true") \
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") 
    
    #for key, value in kwargs.items():
    #    spark_builder = spark_builder.config(key, value)
    
    spark = spark_builder.getOrCreate()

    if kwargs.get('file_format') == "csv":
        # Read Csv S3
        df = spark.read.csv(f"s3a://{bucket_name}/input/data.csv")
    elif kwargs.get('file_format') == "parquet":
        # Read Parquet S3
        df = spark.read.parquet(f"s3a://{bucket_name}/input/data.parquet")
    else:   
        raise ValueError("Invalid file format. Use 'csv' or 'parquet'.")


    # Faire une opération simple
    row_count = df.count()

    

    if kwargs.get('file_format') == "csv":
        # Write to CSV
        df.write.mode("overwrite").csv(f"s3a://{bucket_name}/output/data.csv")
    elif kwargs.get('file_format') == "parquet":
        # Write to S3Parquet
        df.write.mode("overwrite").parquet(f"s3a://{bucket_name}/output/data.parquet")
    else:   
        raise ValueError("Invalid file format. Use 'csv' or 'parquet'.")

    spark.stop()

    return row_count


def example_maxtrix_function(**kwargs):
    # Example function to optimize or test
    operation_type = kwargs.get('operation_type')
    matrix_size = int(kwargs.get('matrix_size'))

    # Create random matrices
    matrice_A = np.random.rand(matrix_size, matrix_size)
    matrice_B = np.random.rand(matrix_size, matrix_size)

    if operation_type == "add": 
        resultat = np.add(matrice_A, matrice_B)
    elif operation_type == "multiply":
        resultat = np.dot(matrice_A, matrice_B)
    else:
        raise ValueError("Invalid operation type. Use 'add' or 'multiply'.")
    return resultat.size


def example_sleep_function(**kwargs):
    sleep_time = kwargs.get('sleep_time')
    time.sleep(sleep_time)
    return 1


with open("config_spark.yaml", "r") as file:
    config_spark = yaml.safe_load(file)

def test_sleep_function():
    # Load configuration
    with open("config_sleep.yaml", "r") as file:
        config_sleep = yaml.safe_load(file)

    # Optuna Optimization
    optuna_optimizer = OptunaOptimizer(example_sleep_function, config_sleep)
    optuna_optimizer.optimize(n_trials=10, direction="minimize")
    print("Best parameters (Optuna):", optuna_optimizer.get_best_params())

    # Test All Combinations
    combination_optimizer = AllCombinationOptimizer(config_sleep)
    results = combination_optimizer.test_combinations(example_sleep_function)
    print("All combinations tested:", combination_optimizer.get_best_combination())


def test_matrix_function():
    # Load configuration
    with open("config_matrix.yaml", "r") as file:
        config_matrix = yaml.safe_load(file)

    # Optuna Optimization
    optuna_optimizer = OptunaOptimizer(example_maxtrix_function, config_matrix)
    optuna_optimizer.optimize(n_trials=10, direction="minimize")
    print("Best parameters (Optuna):", optuna_optimizer.get_best_params())


    # Hyperopt Optimization
    hyperopt_optimizer = HyperoptOptimizer(example_maxtrix_function, config_matrix)
    hyperopt_optimizer.optimize(max_evals=10)
    print("Best parameters (Hyperopt):", hyperopt_optimizer.get_best_params())

    # Test All Combinations
    combination_optimizer = AllCombinationOptimizer(config_matrix)
    results = combination_optimizer.test_combinations(example_maxtrix_function)
    print("All combinations tested:", combination_optimizer.get_best_params())


def test_spark_file_format_function():
    # Load configuration
    with open("config_spark_file_format.yaml", "r") as file:
        config_spark_file_format = yaml.safe_load(file)

    # Optuna Optimization
    #optuna_optimizer = OptunaOptimizer(test_spark_file_format_configuration, config_spark_file_format)
    #optuna_optimizer.optimize(n_trials=10, direction="minimize")

    # Hyperopt Optimization
    hyperopt_optimizer = HyperoptOptimizer(test_spark_file_format_configuration, config_spark_file_format)
    hyperopt_optimizer.optimize(max_evals=10)
    
    # Test All Combinations
    #combination_optimizer = AllCombinationOptimizer(config_spark_file_format)
    #results = combination_optimizer.test_combinations(test_spark_file_format_configuration)

    print("Best parameters (Optuna):", optuna_optimizer.get_best_params())
    print("Best parameters (Hyperopt):", hyperopt_optimizer.get_best_params())
    print("Best parameters (AllCombination):", combination_optimizer.get_best_params())


# Call the functions
#test_sleep_function()
#test_matrix_function()

test_spark_file_format_function()