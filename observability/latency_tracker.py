import time
from typing import Dict
from contextlib import contextmanager

class LatencyTracker:
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.retrieval_latency = 0.0
        self.embedding_latency = 0.0
        self.llm_latency = 0.0
        self.total_latency = 0.0
        self._start_time = None
    
    @contextmanager
    def track(self, operation: str):
        start = time.time()
        try:
            yield
        finally:
            elapsed = time.time() - start
            if operation == 'retrieval':
                self.retrieval_latency += elapsed
            elif operation == 'embedding':
                self.embedding_latency += elapsed
            elif operation == 'llm':
                self.llm_latency += elapsed
            self.total_latency += elapsed
    
    def get_metrics(self) -> Dict:
        return {
            'retrieval_latency': round(self.retrieval_latency, 3),
            'embedding_latency': round(self.embedding_latency, 3),
            'llm_latency': round(self.llm_latency, 3),
            'total_latency': round(self.total_latency, 3)
        }
