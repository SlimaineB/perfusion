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
from pyspark.sql.types import StructType, StructField, IntegerType, StringType, DoubleType

from optimizer.hyperopt_optimizer import HyperoptOptimizer
from optimizer.optuna_optimizer import OptunaOptimizer
from optimizer.allcombination_optimizer import AllCombinationOptimizer
from scenarios.matrix_operation_scenario import MatrixOperationScenario
from scenarios.sleep_scenario import SleepScenario
from scenarios.spark_file_format_scenario import SparkFileFormatScenario



with open("config_spark.yaml", "r") as file:
    config_spark = yaml.safe_load(file)

def test_optimization(scenario_class, config_file, n_trials=10, max_evals=10):
    # Load configuration
    with open(config_file, "r") as file:
        config = yaml.safe_load(file)

    # Initialize scenario
    scenario = scenario_class()

    # Optuna Optimization
    optuna_optimizer = OptunaOptimizer(scenario.run, config)
    optuna_optimizer.optimize(n_trials=n_trials, direction="minimize")

    # Hyperopt Optimization
    hyperopt_optimizer = HyperoptOptimizer(scenario.run, config)
    hyperopt_optimizer.optimize(max_evals=max_evals)

    # Test All Combinations
    combination_optimizer = AllCombinationOptimizer(config)
    results = combination_optimizer.test_combinations(scenario.run)

    # Print results
    print("Best parameters (Optuna):", optuna_optimizer.get_best_params())
    print("Best parameters (Hyperopt):", hyperopt_optimizer.get_best_params())
    print("Best parameters (AllCombination):", combination_optimizer.get_best_params())


def test_sleep_function():
    test_optimization(SleepScenario, "config_sleep.yaml")


def test_matrix_function():
    test_optimization(MatrixOperationScenario, "config_matrix.yaml")


def test_spark_file_format_function():
    test_optimization(SparkFileFormatScenario, "config_spark_file_format.yaml")


# Call the functions
#test_sleep_function()
#test_matrix_function()

test_spark_file_format_function()