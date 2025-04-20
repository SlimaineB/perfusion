

class PerfusionComparator:
    def deployment(self, trial=None):
        """
        Handles the deployment process.
        """
        raise NotImplementedError("This method should be overridden by subclasses.")

    def run(self):
        """
        Executes the comparator logic.
        """
        raise NotImplementedError("This method should be overridden by subclasses.")
