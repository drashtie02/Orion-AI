from typing import Dict
from llm.base_model import BaseModel
import openai
import tiktoken

class OpenAIModel(BaseModel):
    def __init__(self, model_name: str, api_key: str, cost_per_1k_input: float = 0.0, cost_per_1k_output: float = 0.0):
        super().__init__()
        self.model_name = model_name
        self.cost_per_1k_input_tokens = cost_per_1k_input
        self.cost_per_1k_output_tokens = cost_per_1k_output
        openai.api_key = api_key
        try:
            self.encoding = tiktoken.encoding_for_model(model_name)
        except Exception:
            self.encoding = tiktoken.get_encoding("cl100k_base")
    
    def generate(self, prompt: str) -> Dict:
        response = openai.ChatCompletion.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0
        )
        
        return {
            'text': response.choices[0].message.content,
            'tokens_input': response.usage.prompt_tokens,
            'tokens_output': response.usage.completion_tokens,
            'model_name': self.model_name
        }
    
    def count_tokens(self, text: str) -> int:
        return len(self.encoding.encode(text))
