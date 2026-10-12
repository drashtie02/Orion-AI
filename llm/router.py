from llm.base_model import BaseModel
from llm.openai_model import OpenAIModel
from llm.local_model import LocalModel
from llm.api_model import APIModel
from core.config import config
from typing import Dict, Optional

class LLMRouter:
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
        elif model_type == 'local':
            return LocalModel(model_name, 'auto', cost_input, cost_output)
        else:
            raise ValueError(f"Unknown model type: {model_type}")
    
    def _initialize_model(self) -> BaseModel:
        if config.llm_type == 'api' and config.llm_api_url:
            return APIModel(config.llm_api_url, config.llm_model)
        elif config.llm_type == 'openai':
            return OpenAIModel(config.llm_model, config.openai_api_key)
        elif config.llm_type == 'local':
            return LocalModel(config.llm_model, 'auto')
        else:
            raise ValueError(f"Unknown LLM type: {config.llm_type}")
    
    def get_model(self, model_name: str) -> Optional[BaseModel]:
        return self.models.get(model_name)
    
    def generate(self, prompt: str, model_name: Optional[str] = None):
        if model_name and model_name in self.models:
            return self.models[model_name].generate(prompt)
        return self.model.generate(prompt)
    
    def count_tokens(self, text: str) -> int:
        return self.model.count_tokens(text)
