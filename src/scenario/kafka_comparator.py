# kafka_comparator.py
from scenario.perfusion_comparator import PerfusionComparator

class KafkaComparator(PerfusionComparator ):
    def deployment(self, trial=None):
        """
        Handles the deployment process for the Kafka comparator.
        """
        print("Deploying Kafka Comparator...")

    def run(self):
        """
        Executes the Kafka comparator logic.
        """
        print("Running Kafka Comparator...")

# Example usage
if __name__ == "__main__":
    comparator = KafkaComparator()
    comparator.deployment()
    comparator.run()