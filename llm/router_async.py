from llm.base_model_async import BaseModel
from llm.openai_model_async import OpenAIModel
from llm.api_model_async import APIModel
from core.config import config
from typing import Dict, Optional, AsyncIterator

class LLMRouterAsync:
    def __init__(self, model_configs: Optional[Dict] = None):
        self.models = {}
        self.model_name = None
        
        if model_configs:
            for name, cfg in model_configs.items():
                self.models[name] = self._create_model(cfg)
            self.model = list(self.models.values())[0] if self.models else self._initialize_model()
            self.model_name = self.model.model_name
        else:
            self.model = self._initialize_model()
            self.model_name = self.model.model_name
    
    def _create_model(self, cfg: Dict) -> BaseModel:
        model_type = cfg.get('type', 'api')
        model_name = cfg.get('model_name', 'default')
        cost_input = cfg.get('cost_per_1k_input', 0.0)
        cost_output = cfg.get('cost_per_1k_output', 0.0)
        
        if model_type == 'openai':
            return OpenAIModel(model_name, config.openai_api_key, cost_input, cost_output)
        elif model_type == 'api':
            api_url = cfg.get('api_url', config.llm_api_url)
            return APIModel(api_url, model_name, cost_input, cost_output)
        else:
            raise ValueError(f"Unknown model type: {model_type}")
    
    def _initialize_model(self) -> BaseModel:
        if config.llm_type == 'api' and config.llm_api_url:
            return APIModel(config.llm_api_url, config.llm_model)
        elif config.llm_type == 'openai':
            return OpenAIModel(config.llm_model, config.openai_api_key)
        else:
            raise ValueError(f"Unknown LLM type: {config.llm_type}")
    
    def get_model(self, model_name: str) -> Optional[BaseModel]:
        return self.models.get(model_name)
    
    async def generate(self, prompt: str, model_name: Optional[str] = None, stream: bool = False):
        if model_name and model_name in self.models:
            return await self.models[model_name].generate(prompt, stream=stream)
        return await self.model.generate(prompt, stream=stream)
    
    async def generate_stream(self, prompt: str, model_name: Optional[str] = None) -> AsyncIterator[str]:
        if model_name and model_name in self.models:
            async for chunk in self.models[model_name].generate_stream(prompt):
                yield chunk
        else:
            async for chunk in self.model.generate_stream(prompt):
                yield chunk
    
    def count_tokens(self, text: str) -> int:
        return self.model.count_tokens(text)
    
    async def close(self):
        for model in self.models.values():
            if hasattr(model, 'close'):
                await model.close()
        if hasattr(self.model, 'close'):
            await self.model.close()
