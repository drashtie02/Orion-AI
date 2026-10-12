from typing import Dict, AsyncIterator
from llm.base_model_async import BaseModel
import httpx
import json

class APIModel(BaseModel):
    def __init__(self, api_url: str, model_name: str, cost_per_1k_input: float = 0.0, cost_per_1k_output: float = 0.0):
        super().__init__()
        self.api_url = api_url
        self.model_name = model_name
        self.cost_per_1k_input_tokens = cost_per_1k_input
        self.cost_per_1k_output_tokens = cost_per_1k_output
        self._client = httpx.AsyncClient(timeout=120.0)
        self._circuit_breaker.name = f"llm_api_{model_name}"
    
    async def generate(self, prompt: str, stream: bool = False) -> Dict:
        if stream:
            raise ValueError("Use generate_stream for streaming responses")
        
        async def _call():
            response = await self._client.post(
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
        
        async def _call_with_retry():
            return await self._retry_config_wrapper(_call)
        
        return await self._circuit_breaker.call(_call_with_retry)
    
    async def generate_stream(self, prompt: str) -> AsyncIterator[str]:
        async def _stream():
            async with self._client.stream(
                'POST',
                self.api_url,
                json={"model": self.model_name, "prompt": prompt, "stream": True}
            ) as response:
                if response.status_code != 200:
                    raise Exception(f"API request failed with status {response.status_code}")
                
                async for line in response.aiter_lines():
                    if line.strip():
                        try:
                            data = json.loads(line)
                            if 'response' in data:
                                yield data['response']
                        except json.JSONDecodeError:
                            continue
        
        async for chunk in _stream():
            yield chunk
    
    async def _retry_config_wrapper(self, func):
        from core.resilience import retry_with_backoff
        decorated = retry_with_backoff(self._retry_config)(func)
        return await decorated()
    
    def count_tokens(self, text: str) -> int:
        return len(text.split())
    
    async def close(self):
        await self._client.aclose()
