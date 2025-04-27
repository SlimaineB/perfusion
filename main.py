import optuna
import numpy as np
import os
import time
import psutil
import sys

from comparator.perfusion_comparator import PerfusionComparator
from comparator.matrix_comparator import MatrixComparator

# TO Fix import issue
#sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Fixer une graine pour Optuna
comparator:PerfusionComparator = MatrixComparator()

# Init Benchmark environment
def setup(trial) -> int:
    comparator.deployment(trial)

# Clenup Benchmark environment
def cleanup(trial) -> None:
    pass

def runBenchmark():
    comparator.run()

# Fonction d'objectif pour Optuna
def objectif(trial):
    # Initialiser l'environnement
    nombre_threads = setup(trial)

    # Collect metrics
    processus = psutil.Process(os.getpid())
    debut = time.time()
    cpu_avant = processus.cpu_percent(interval=None)  # Charge CPU du processus
    ram_avant = processus.memory_info().rss / (1024 * 1024)  # RAM utilisée en Mo

    # Run the benchmark
    runBenchmark()  

    # Surveiller les ressources après l'opération
    fin = time.time()
    cpu_apres = processus.cpu_percent(interval=None)  # Charge CPU du processus
    ram_apres = processus.memory_info().rss / (1024 * 1024)

    # Calculs des métriques
    temps_execution = (fin - debut) * 1000  # Temps en millisecondes
    charge_cpu = cpu_apres - cpu_avant  # Différence d'utilisation CPU
    consommation_ram = ram_apres - ram_avant  # Différence d'utilisation RAM

    # Pondérations pour le score
    pond_time = 0.5
    pond_cpu = 0.3
    pond_ram = 0.2

    # Calculer le score final
    score = (pond_time * temps_execution) + (pond_cpu * charge_cpu) + (pond_ram * consommation_ram)

    # Afficher les résultats
    print(f"Threads : {nombre_threads}, Temps : {temps_execution:.2f} ms, CPU : {charge_cpu:.2f} %, RAM : {consommation_ram:.2f} Mo, Score : {score:.2f}")
    return score


etude = optuna.create_study(direction="minimize", sampler=optuna.samplers.TPESampler(seed=42))
etude.optimize(objectif, n_trials=20)

# Résultats
print("Meilleure configuration trouvée :")
print("Nombre de threads :", etude.best_params["threads"])
print("Score minimal :", etude.best_value)

