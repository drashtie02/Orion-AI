import yaml
import os
from pathlib import Path
from typing import Optional, Dict

DEFAULT_EVALUATION_WEIGHTS = {
    'faithfulness': 0.3,
    'relevance': 0.2,
    'hallucination': 0.3,
    'source_coverage': 0.2
}

DEFAULT_ROUTING_CONFIG = {
    'cheap_model': 'cheap_model',
    'strong_model': 'strong_model',
    'token_threshold': 500,
    'confidence_threshold': 0.6
}

DEFAULT_RESILIENCE_CONFIG = {
    'retry': {
        'max_retries': 3,
        'base_delay': 1.0,
        'max_delay': 30.0
    },
    'circuit_breaker': {
        'failure_threshold': 5,
        'recovery_timeout': 60.0,
        'window_size': 10
    }
}

class Config:
    def __init__(self, config_path: Optional[str] = None):
        config_data = self._load_config(config_path)
        
        self.embedding_model = config_data.get('embedding_model', 'sentence-transformers/all-MiniLM-L6-v2')
        self.embedding_api_url = config_data.get('embedding_api_url', '')
        self.embedding_type = config_data.get('embedding_type', 'local')
        self.llm_model = config_data.get('llm_model', 'gpt-3.5-turbo')
        self.llm_api_url = config_data.get('llm_api_url', '')
        self.llm_type = config_data.get('llm_type', 'openai')
        self.retrieval_alpha = config_data.get('retrieval_alpha', 0.5)
        self.top_k_default = config_data.get('top_k_default', 5)
        self.max_context_tokens = config_data.get('max_context_tokens', 2048)
        self.device = config_data.get('device', 'auto')
        self.chunk_size = config_data.get('chunk_size', 512)
        self.chunk_overlap = config_data.get('chunk_overlap', 0.2)
        self.openai_api_key = config_data.get('openai_api_key', '')
        self.index_path = config_data.get('index_path', 'artifacts/index')
        self.use_mixed_precision = config_data.get('use_mixed_precision', True)
        self.cpu_batch_size = config_data.get('cpu_batch_size', 8)
        self.gpu_batch_size = config_data.get('gpu_batch_size', 32)
        self.evaluation_weights = config_data.get('evaluation_weights', DEFAULT_EVALUATION_WEIGHTS)
        self.critic_threshold = config_data.get('critic_threshold', 0.6)
        self.models = config_data.get('models', {})
        self.monthly_budget_limit = config_data.get('monthly_budget_limit', 1000.0)
        self.routing_config = config_data.get('routing_config', DEFAULT_ROUTING_CONFIG)
        self.resilience = config_data.get('resilience', DEFAULT_RESILIENCE_CONFIG)
        
        self.redis_enabled = os.getenv('REDIS_ENABLED', 'false').lower() == 'true'
        self.redis_host = os.getenv('REDIS_HOST', 'localhost')
        self.redis_port = int(os.getenv('REDIS_PORT', '6379'))
        self.redis_db = int(os.getenv('REDIS_DB', '0'))
        self.cache_ttl = int(os.getenv('CACHE_TTL', '3600'))
        
        self.rate_limit_enabled = os.getenv('RATE_LIMIT_ENABLED', 'true').lower() == 'true'
        self.rate_limit_requests = int(os.getenv('RATE_LIMIT_REQUESTS', '100'))
        self.rate_limit_window = int(os.getenv('RATE_LIMIT_WINDOW_SECONDS', '60'))
        
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        self.environment = os.getenv('ENVIRONMENT', 'production')
    
    def _load_config(self, config_path: Optional[str]) -> Dict:
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                return yaml.safe_load(f) or {}
        return {}

config = Config('config.yaml')
