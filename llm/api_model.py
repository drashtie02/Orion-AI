from typing import Dict
from llm.base_model import BaseModel
import requests

class APIModel(BaseModel):
    def __init__(self, api_url: str, model_name: str, cost_per_1k_input: float = 0.0, cost_per_1k_output: float = 0.0):
        super().__init__()
        self.api_url = api_url
        self.model_name = model_name
        self.cost_per_1k_input_tokens = cost_per_1k_input
        self.cost_per_1k_output_tokens = cost_per_1k_output
    
    def generate(self, prompt: str) -> Dict:
        response = requests.post(
            self.api_url,
            json={"model": self.model_name, "prompt": prompt, "stream": False}
        )
        
        if response.status_code != 200:
            raise Exception(f"API request failed with status {response.status_code}")
        
        data = response.json()
        text = data.get('response', '')
        
        input_tokens = len(prompt.split())
        output_tokens = len(text.split())
        
        return {
            'text': text,
            'tokens_input': input_tokens,
            'tokens_output': output_tokens,
            'model_name': self.model_name
        }
    
    def count_tokens(self, text: str) -> int:
        return len(text.split())
