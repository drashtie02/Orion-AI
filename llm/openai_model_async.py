from typing import Dict, AsyncIterator, Optional
from llm.base_model_async import BaseModel
import httpx
import json

class OpenAIModel(BaseModel):
    def __init__(self, model_name: str, api_key: str, cost_per_1k_input: float = 0.0, cost_per_1k_output: float = 0.0):
        super().__init__()
        self.model_name = model_name
        self.api_key = api_key
        self.cost_per_1k_input_tokens = cost_per_1k_input
        self.cost_per_1k_output_tokens = cost_per_1k_output
        self._client = httpx.AsyncClient(
            timeout=120.0,
            headers={"Authorization": f"Bearer {api_key}"}
        )
        self._circuit_breaker.name = f"llm_openai_{model_name}"
    
    async def generate(self, prompt: str, stream: bool = False) -> Dict:
        if stream:
            raise ValueError("Use generate_stream for streaming responses")
        
        async def _call():
            response = await self._client.post(
                "https://api.openai.com/v1/chat/completions",
                json={
                    "model": self.model_name,
                    "messages": [{"role": "user", "content": prompt}],
                    "stream": False
                }
            )
            
            if response.status_code != 200:
                raise Exception(f"OpenAI API failed with status {response.status_code}")
            
            data = response.json()
            text = data['choices'][0]['message']['content']
            usage = data.get('usage', {})
            
            return {
                'text': text,
                'tokens_input': usage.get('prompt_tokens', 0),
                'tokens_output': usage.get('completion_tokens', 0),
                'model_name': self.model_name
            }
        
        return await self._circuit_breaker.call(
            self._retry_config_wrapper(_call)
        )
    
    async def generate_stream(self, prompt: str) -> AsyncIterator[str]:
        async def _stream():
            async with self._client.stream(
                'POST',
                "https://api.openai.com/v1/chat/completions",
                json={
                    "model": self.model_name,
                    "messages": [{"role": "user", "content": prompt}],
                    "stream": True
                }
            ) as response:
                if response.status_code != 200:
                    raise Exception(f"OpenAI API failed with status {response.status_code}")
                
                async for line in response.aiter_lines():
                    if line.startswith('data: '):
                        line = line[6:]
                        if line.strip() == '[DONE]':
                            break
                        try:
                            data = json.loads(line)
                            delta = data['choices'][0]['delta']
                            if 'content' in delta:
                                yield delta['content']
                        except json.JSONDecodeError:
                            continue
        
        async for chunk in _stream():
            yield chunk
    
    async def _retry_config_wrapper(self, func):
        from core.resilience import retry_with_backoff
        decorated = retry_with_backoff(self._retry_config)(func)
        return await decorated()
    
    def count_tokens(self, text: str) -> int:
        try:
            import tiktoken
            encoding = tiktoken.encoding_for_model(self.model_name)
            return len(encoding.encode(text))
        except:
            return len(text.split())
    
    async def close(self):
        await self._client.aclose()
