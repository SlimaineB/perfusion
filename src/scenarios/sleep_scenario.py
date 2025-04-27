import time
from .base_scenario import BaseScenario

class SleepScenario(BaseScenario):
    def __init__(self):
        super().__init__()

    def run(self, **params):
        """
        Implémentation de la méthode run pour le scénario Sleep.
        """
        print("Running SleepScenario with params:", params)
        sleep_time = params.get('sleep_time', 1)  # Temps de sommeil par défaut : 1 seconde
        time.sleep(sleep_time)
        return sleep_time