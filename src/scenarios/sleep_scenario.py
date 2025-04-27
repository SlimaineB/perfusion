import time

class SleepScenario:
    def run(self, **kwargs):
        sleep_time = kwargs.get('sleep_time')
        time.sleep(sleep_time)
        return 1