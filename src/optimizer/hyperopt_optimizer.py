from hyperopt import fmin, tpe, hp, Trials, STATUS_OK
import numpy as np
import pandas as pd
from utils.timer import time_function_execution  # Importer la fonction timer

class HyperoptOptimizer:
    """
    Class to optimize parameters using Hyperopt.
    """
    def __init__(self, objective_function, config):
        """
        Initialize the Hyperopt optimizer.

        :param objective_function: The function to optimize.
        :param config: The parameter configuration from the config.yaml file.
        """
        self.objective_function = objective_function
        self.config = config
        self.best_params = None
        self.trials = Trials()

    def define_search_space(self):
        """
        Define the search space for Hyperopt based on the config.
        """
        search_space = {}
        for key, value in self.config.items():
            if value['type'] == 'list':
                search_space[key] = hp.choice(key, value['values'])
            elif value['type'] == 'range':
                search_space[key] = hp.quniform(key, value['min'], value['max'], value['step'])
        return search_space

    def optimize(self, max_evals=50):
        """
        Run the optimization process.

        :param max_evals: Number of evaluations for optimization.
        """
        search_space = self.define_search_space()

        def wrapped_objective(params):
            # Mesurer le temps d'exécution de la fonction objective
            _, elapsed_time = time_function_execution(self.objective_function, **params)
            print(f"Tested parameters: {params}, Execution time: {elapsed_time:.4f} seconds")  # Log des paramètres testés
            return {
                'loss': elapsed_time,  # Hyperopt minimise la valeur de 'loss'
                'status': STATUS_OK,  # Indique que l'essai s'est terminé correctement
                'params': params  # Ajout des paramètres pour les logs
            }

        self.best_params = fmin(
            fn=wrapped_objective,
            space=search_space,
            algo=tpe.suggest,
            max_evals=max_evals,
            trials=self.trials
        )

        # Afficher les logs détaillés après l'optimisation
        #print("\nDetailed trial results:")
        #for i, trial in enumerate(self.trials.trials):
        #    print(f"Trial {i + 1}:")
        #    print(f"  Parameters: {trial['result']['params']}")
        #    print(f"  Loss (Execution Time): {trial['result']['loss']:.4f} seconds")
        #    print(f"  Status: {trial['result']['status']}")

    def trials_to_dataframe(self) -> pd.DataFrame:
        data = []
        for trial in self.trials.trials:
            trial_data = trial["misc"]["vals"]
            trial_data = {k: v[0] for k, v in trial_data.items()}  # Extraire les valeurs
            trial_data["score"] = trial["result"]["loss"]
            trial_data["trial_number"] = trial["tid"]
            data.append(trial_data)
        return pd.DataFrame(data)

    def get_best_params(self):
        """
        Get the best parameters found by Hyperopt.
        """
        if self.best_params is None:
            raise ValueError("No optimization has been run yet.")
        
        # Convertir les types NumPy en types natifs Python et gérer hp.choice
        converted_params = {}
        for key, value in self.best_params.items():
            if key in self.config and self.config[key]['type'] == 'list':
                # Mapper l'indice à la valeur réelle pour hp.choice
                converted_params[key] = self.config[key]['values'][int(value)]
            else:
                # Convertir les types NumPy en types natifs Python
                converted_params[key] = (int(value) if isinstance(value, (np.integer, np.int64)) else
                                         float(value) if isinstance(value, (np.floating, np.float64)) else
                                         value)
        return converted_params