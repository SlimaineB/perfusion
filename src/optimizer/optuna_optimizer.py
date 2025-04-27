import optuna
from optimizer.base_optimizer import BaseOptimizer
from utils.timer import time_function_execution  # Importer la fonction depuis timer.py


class OptunaOptimizer(BaseOptimizer):
    """
    Class to optimize parameters using Optuna.
    """
    def __init__(self, objective_function, config, sampler=None, pruner=None):
        """
        Initialize the Optuna optimizer.

        :param objective_function: The function to optimize.
        :param config: The parameter configuration from the config.yaml file.
        :param sampler: The Optuna sampler to use (default: TPESampler).
        :param pruner: The Optuna pruner to use (default: None).
        """
        super().__init__(config)
        self.objective_function = objective_function
        self.sampler = sampler or optuna.samplers.TPESampler(seed=42)
        self.pruner = pruner
        self.study = None

    def define_search_space(self, trial):
        """
        Define the search space for Optuna based on the config.
        """
        params = {}
        for key, value in self.config.items():
            if value['type'] == 'list':
                params[key] = trial.suggest_categorical(key, value['values'])
            elif value['type'] == 'range':
                params[key] = trial.suggest_int(key, value['min'], value['max'], step=value['step'])
        return params

    def optimize(self, n_trials=50, direction="minimize"):
        """
        Run the optimization process.

        :param n_trials: Number of trials for optimization.
        :param direction: Optimization direction ("minimize" or "maximize").
        """
        def wrapped_objective(trial):
            params = self.define_search_space(trial)
            _, elapsed_time = time_function_execution(self.objective_function, **params)  # Utiliser time_function_execution
            return elapsed_time  # Retourner le temps comme score

        self.study = optuna.create_study(direction=direction, sampler=self.sampler, pruner=self.pruner, study_name= "optuna_study", storage="sqlite:///example.db", load_if_exists=True)
        self.study.optimize(wrapped_objective, n_trials=n_trials)

    def get_best_params(self):
        """
        Get the best parameters found by Optuna.
        """
        if self.study is None:
            raise ValueError("No study has been run yet.")
        return self.study.best_params