import random
import optuna
import numpy as np
import os
import time
import psutil
import sys
import yaml

from comparator.perfusion_comparator import PerfusionComparator
from comparator.matrix_comparator import MatrixComparator
from optimizer.optuna_optimizer import OptunaOptimizer
from optimizer.allcombination_optimizer import AllCombinationOptimizer



def example_maxtrix_function(**kwargs):
    # Example function to optimize or test
    operation_type = kwargs.get('operation_type')
    matrix_size = kwargs.get('matrix_size')

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
    combination_tester = AllCombinationOptimizer(config_sleep)
    results = combination_tester.test_combinations(example_sleep_function)
    print("All combinations tested:", combination_tester.get_best_combination())


def test_matrix_function():
    # Load configuration
    with open("config_matrix.yaml", "r") as file:
        config_matrix = yaml.safe_load(file)

    # Optuna Optimization
    optuna_optimizer = OptunaOptimizer(example_maxtrix_function, config_matrix)
    optuna_optimizer.optimize(n_trials=10, direction="minimize")
    print("Best parameters (Optuna):", optuna_optimizer.get_best_params())

    # Test All Combinations
    combination_tester = AllCombinationOptimizer(config_matrix)
    results = combination_tester.test_combinations(example_maxtrix_function)
    print("All combinations tested:", combination_tester.get_best_params())


# Call the functions
#test_sleep_function()
test_matrix_function()