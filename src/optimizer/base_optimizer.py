class BaseOptimizer:
    """
    Base class for all optimizers.
    """
    def __init__(self, config):
        """
        Initialize the optimizer with the provided configuration.

        :param config: The parameter configuration from the config.yaml file.
        """
        self.config = config

    def parse_config(self):
        """
        Parse the configuration to extract parameter definitions.
        """
        parsed_config = {}
        for key, value in self.config.items():
            if value['type'] == 'list':
                parsed_config[key] = value['values']
            elif value['type'] == 'range':
                parsed_config[key] = self.generate_range(
                    value['min'], value['max'], value['step'], value.get('unit')
                )
        return parsed_config

    def generate_range(self, min_val, max_val, step, unit=None):
        """
        Generate a range of values based on the configuration.
        """
        range_values = list(range(min_val, max_val + 1, step))
        if unit:
            range_values = [f"{val}{unit}" for val in range_values]
        return range_values