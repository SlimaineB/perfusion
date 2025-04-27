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



def example_function(**kwargs):
    # Example function to optimize or test
    taille_matrice = 100 * kwargs.get('spark.executor.memory')
    print(f"Testing with parameters: {kwargs}")
    print(f"Matrix size: {kwargs.get('spark.executor.memory')}")
    matrice_A = np.random.rand(taille_matrice, taille_matrice)
    matrice_B = np.random.rand(taille_matrice, taille_matrice)

    # Multiplication matricielle
    resultat = np.dot(matrice_A, matrice_B)
    return 1


# Load configuration
with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

# Optuna Optimization
optuna_optimizer = OptunaOptimizer(example_function, config)
optuna_optimizer.optimize(n_trials=10, direction="minimize")
print("Best parameters (Optuna):", optuna_optimizer.get_best_params())

# Test All Combinations
combination_tester = AllCombinationOptimizer(config)
results = combination_tester.test_combinations(example_function)
print("All combinations tested:", combination_tester.get_best_combination())

