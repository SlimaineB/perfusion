from itertools import product

import pandas as pd
from optimizer.base_optimizer import BaseOptimizer
from utils.timer import time_function_execution


class AllCombinationOptimizer(BaseOptimizer):
    """
    Class to test all possible parameter combinations.
    """
    def __init__(self, func, config):
        """
        Initialize the AllCombinationOptimizer.

        :param config: The parameter configuration from the config.yaml file.
        """
        super().__init__(config)
        self.func = func
        self.combinations = self.generate_combinations()
        self.best_combination = None
        self.best_execution_time = 10000
        self.results = []

    def generate_combinations(self):
        """
        Generate all possible combinations of parameters based on the config.
        """
        param_names = []
        param_values = []


        for key, value in self.config.items():
            param_names.append(key)
            if value['type'] == 'list':
                param_values.append(value['values'])
            elif value['type'] == 'range':
                param_values.append(range(value['min'], value['max'] + 1, value['step']))

        return [dict(zip(param_names, combination)) for combination in product(*param_values)]

    def optimize(self):
        """
        Test all combinations of parameters with the given function.

        :param func: The function to test.
        """
        
        best_execution_time = 0
        for combination in self.combinations:
            #print(f"Testing combination {combination} ")
            result, execution_time = time_function_execution(self.func, **combination)
            #print(f"Tested combination {combination} executed in {execution_time:.4f} seconds.")
            if(execution_time < self.best_execution_time ):
                #print(f"Best execution time so far: {best_execution_time:.4f} seconds.")
                self.best_combination = combination
                self.best_execution_time = execution_time
            self.results.append((combination, result, execution_time))

    

    def trials_to_dataframe(self) -> pd.DataFrame:
        """
        Convert the results of all tested combinations into a pandas DataFrame.

        :return: A DataFrame containing all tested combinations with their scores and execution times.
        """
        data = []
        for i, (combination, result, execution_time) in enumerate(self.results):
            trial_data = combination.copy()
            trial_data["score"] = execution_time
            trial_data["trial_number"] = i
            data.append(trial_data)
        return pd.DataFrame(data)

    def get_best_params(self): 
        """
        Get the best combination found during testing.
        """
        if self.best_combination is None:
            raise ValueError("No combinations have been tested yet.")
        return self.best_combination
    
    def get_best_execution_time(self):
        return self.best_execution_time
