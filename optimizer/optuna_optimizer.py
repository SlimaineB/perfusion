
from optimizer.perfusion_optimiser import PerfusionOptimizer


class OptunaOptimizer(PerfusionOptimizer):
    """
    Class to optimize perfusion parameters for a given set of data using Optuna.
    """
    def __init__(self, data):
        """
        Initialize the optimizer with the provided data.

        :param data: The data to be used for optimization.
        """
        super().__init__(data)
        self.optimized_parameters = None
        self.study = None
        self.sampler = None
        self.pruner = None
        self.objective_function = None
        self.n_trials = 20
        self.direction = "minimize"
        self.study_name = "optina_study"


if __name__ == "__main__":
    # Example usage
    data = {"example_data": 123}
    optimizer = OptunaOptimizer(data)
    optimizer.optimize()
    print(optimizer.get_optimized_parameters())