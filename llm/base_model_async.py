from abc import ABC, abstractmethod
from typing import Dict, AsyncIterator
from core.resilience import CircuitBreaker, retry_with_backoff, RetryConfig

class BaseModel(ABC):
    def __init__(self):
        self.cost_per_1k_input_tokens = 0.0
        self.cost_per_1k_output_tokens = 0.0
        self.max_tokens = 4096
        self.model_name = "unknown"
        self._circuit_breaker = CircuitBreaker(
            name=f"llm_{self.model_name}",
        )
        self._retry_config = RetryConfig(max_retries=3, base_delay=1.0, max_delay=30.0)
    
    @abstractmethod
    async def generate(self, prompt: str, stream: bool = False) -> Dict:
        pass
    
    @abstractmethod
    async def generate_stream(self, prompt: str) -> AsyncIterator[str]:
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
