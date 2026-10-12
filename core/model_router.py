from typing import Dict
from core.logging import setup_logger

logger = setup_logger(__name__)

MAX_LATENCY_HISTORY = 100

class ModelRouter:
    def __init__(self, llm_router, cheap_model: str, strong_model: str, 
                 token_threshold: int = 500, confidence_threshold: float = 0.6):
        self.llm_router = llm_router
        self.cheap_model = cheap_model
        self.strong_model = strong_model
        self.token_threshold = token_threshold
        self.confidence_threshold = confidence_threshold
        self.latency_history = {cheap_model: [], strong_model: []}
        self.max_latency_threshold = 10.0
    
    def select_initial_model(self, task_type: str, reasoning_depth: str, estimated_tokens: int) -> str:
        depth = int(reasoning_depth) if isinstance(reasoning_depth, str) and reasoning_depth.isdigit() else 0
        
        if task_type == "multi-hop" or depth >= 3:
            return self.strong_model
        
        if estimated_tokens > self.token_threshold:
            return self.strong_model
        
        return self.cheap_model
    
    def should_escalate(self, confidence_score: float, initial_model: str) -> bool:
        if initial_model == self.strong_model:
            return False
        
        if confidence_score < self.confidence_threshold:
            avg_latency = self._get_avg_latency(self.strong_model)
            if avg_latency > self.max_latency_threshold and confidence_score >= 0.3:
                return False
            return True
        
        return False
    
    def record_latency(self, model_name: str, latency: float):
        if model_name in self.latency_history:
            self.latency_history[model_name].append(latency)
            if len(self.latency_history[model_name]) > MAX_LATENCY_HISTORY:
                self.latency_history[model_name].pop(0)
    
    def _get_avg_latency(self, model_name: str) -> float:
        if model_name in self.latency_history and self.latency_history[model_name]:
            return sum(self.latency_history[model_name]) / len(self.latency_history[model_name])
        return 0.0
