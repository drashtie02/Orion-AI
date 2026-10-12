from typing import Dict
import time

class MetricsCollector:
    def __init__(self):
        self.metrics = {}
    
    def record(self, metric_name: str, value: float):
        if metric_name not in self.metrics:
            self.metrics[metric_name] = []
        self.metrics[metric_name].append(value)
    
    def get_metrics(self) -> Dict:
        return self.metrics
