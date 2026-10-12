from abc import ABC, abstractmethod
from typing import Dict

class BaseModel(ABC):
    def __init__(self):
        self.cost_per_1k_input_tokens = 0.0
        self.cost_per_1k_output_tokens = 0.0
        self.max_tokens = 4096
        self.model_name = "unknown"
    
    @abstractmethod
    def generate(self, prompt: str) -> Dict:
        pass
    
    @abstractmethod
    def count_tokens(self, text: str) -> int:
        pass
    
    def get_cost_info(self) -> Dict:
        return {
            'model_name': self.model_name,
            'cost_per_1k_input': self.cost_per_1k_input_tokens,
            'cost_per_1k_output': self.cost_per_1k_output_tokens,
            'max_tokens': self.max_tokens
        }
