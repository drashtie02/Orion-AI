from typing import Dict
import json
from pathlib import Path

class TokenTracker:
    def __init__(self):
        self.reset()
        self.cumulative_cost = self._load_cumulative_cost()
    
    def reset(self):
        self.input_tokens = 0
        self.output_tokens = 0
        self.total_tokens = 0
        self.estimated_cost = 0.0
        self.model_used = ""
    
    def track(self, input_tokens: int, output_tokens: int, model_name: str = "", cost_per_1k_input: float = 0.0, cost_per_1k_output: float = 0.0):
        self.input_tokens += input_tokens
        self.output_tokens += output_tokens
        self.total_tokens += input_tokens + output_tokens
        self.model_used = model_name
        
        if cost_per_1k_input > 0 or cost_per_1k_output > 0:
            cost = (input_tokens / 1000.0) * cost_per_1k_input + (output_tokens / 1000.0) * cost_per_1k_output
        else:
            cost = self._estimate_cost(input_tokens, output_tokens, model_name)
        
        self.estimated_cost += cost
        self.cumulative_cost += cost
    
    def _estimate_cost(self, input_tokens: int, output_tokens: int, model_name: str) -> float:
        pricing = {
            'gpt-3.5-turbo': {'input': 0.0015 / 1000, 'output': 0.002 / 1000},
            'gpt-4': {'input': 0.03 / 1000, 'output': 0.06 / 1000},
        }
        if model_name in pricing:
            return input_tokens * pricing[model_name]['input'] + output_tokens * pricing[model_name]['output']
        return 0.0
    
    def get_metrics(self) -> Dict:
        return {
            'input_tokens': self.input_tokens,
            'output_tokens': self.output_tokens,
            'total_tokens': self.total_tokens,
            'estimated_cost': round(self.estimated_cost, 6),
            'model_used': self.model_used
        }
    
    def get_cumulative_cost(self) -> float:
        return self.cumulative_cost
    
    def save_cumulative_cost(self):
        path = Path("artifacts/cost_tracking.json")
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            json.dump({'cumulative_cost': self.cumulative_cost}, f)
    
    def _load_cumulative_cost(self) -> float:
        path = Path("artifacts/cost_tracking.json")
        if path.exists():
            try:
                with open(path, 'r') as f:
                    return json.load(f).get('cumulative_cost', 0.0)
            except Exception:
                return 0.0
        return 0.0
