import pytest
from unittest.mock import patch, mock_open
import yaml
from pathlib import Path
from core.config import Config, DEFAULT_EVALUATION_WEIGHTS, DEFAULT_ROUTING_CONFIG, DEFAULT_RESILIENCE_CONFIG

class TestConfig:
    def test_initialization_with_defaults(self):
        with patch('core.config.Path.exists', return_value=False):
            config = Config()
            
            assert config.embedding_model == 'sentence-transformers/all-MiniLM-L6-v2'
            assert config.llm_model == 'gpt-3.5-turbo'
            assert config.retrieval_alpha == 0.5
            assert config.top_k_default == 5
    
    def test_initialization_with_config_file(self):
        config_data = {
            'embedding_model': 'custom-model',
            'llm_model': 'gpt-4',
            'retrieval_alpha': 0.7,
            'top_k_default': 10
        }
        
        with patch('builtins.open', mock_open(read_data=yaml.dump(config_data))):
            with patch('core.config.Path.exists', return_value=True):
                config = Config('test_config.yaml')
                
                assert config.embedding_model == 'custom-model'
                assert config.llm_model == 'gpt-4'
                assert config.retrieval_alpha == 0.7
                assert config.top_k_default == 10
    
    def test_initialization_with_empty_config_file(self):
        with patch('builtins.open', mock_open(read_data='')):
            with patch('core.config.Path.exists', return_value=True):
                config = Config('test_config.yaml')
                
                assert config.embedding_model == 'sentence-transformers/all-MiniLM-L6-v2'
    
    def test_initialization_with_nonexistent_file(self):
        with patch('core.config.Path.exists', return_value=False):
            config = Config('nonexistent.yaml')
            
            assert config.embedding_model == 'sentence-transformers/all-MiniLM-L6-v2'
    
    def test_environment_variables_override(self):
        with patch.dict('os.environ', {
            'REDIS_ENABLED': 'true',
            'REDIS_HOST': 'custom-redis',
            'REDIS_PORT': '6380',
            'REDIS_DB': '1',
            'CACHE_TTL': '7200',
            'RATE_LIMIT_ENABLED': 'false',
            'RATE_LIMIT_REQUESTS': '200',
            'RATE_LIMIT_WINDOW_SECONDS': '120',
            'LOG_LEVEL': 'DEBUG',
            'ENVIRONMENT': 'development'
        }):
            with patch('core.config.Path.exists', return_value=False):
                config = Config()
                
                assert config.redis_enabled is True
                assert config.redis_host == 'custom-redis'
                assert config.redis_port == 6380
                assert config.redis_db == 1
                assert config.cache_ttl == 7200
                assert config.rate_limit_enabled is False
                assert config.rate_limit_requests == 200
                assert config.rate_limit_window == 120
                assert config.log_level == 'DEBUG'
                assert config.environment == 'development'
    
    def test_default_evaluation_weights(self):
        with patch('core.config.Path.exists', return_value=False):
            config = Config()
            
            assert config.evaluation_weights == DEFAULT_EVALUATION_WEIGHTS
    
    def test_custom_evaluation_weights(self):
        custom_weights = {
            'faithfulness': 0.4,
            'relevance': 0.3,
            'hallucination': 0.2,
            'source_coverage': 0.1
        }
        config_data = {'evaluation_weights': custom_weights}
        
        with patch('builtins.open', mock_open(read_data=yaml.dump(config_data))):
            with patch('core.config.Path.exists', return_value=True):
                config = Config('test_config.yaml')
                
                assert config.evaluation_weights == custom_weights
    
    def test_default_routing_config(self):
        with patch('core.config.Path.exists', return_value=False):
            config = Config()
            
            assert config.routing_config == DEFAULT_ROUTING_CONFIG
    
    def test_custom_routing_config(self):
        custom_routing = {
            'cheap_model': 'llama2',
            'strong_model': 'gpt-4',
            'token_threshold': 1000,
            'confidence_threshold': 0.8
        }
        config_data = {'routing_config': custom_routing}
        
        with patch('builtins.open', mock_open(read_data=yaml.dump(config_data))):
            with patch('core.config.Path.exists', return_value=True):
                config = Config('test_config.yaml')
                
                assert config.routing_config == custom_routing
    
    def test_default_resilience_config(self):
        with patch('core.config.Path.exists', return_value=False):
            config = Config()
            
            assert config.resilience == DEFAULT_RESILIENCE_CONFIG
    
    def test_custom_resilience_config(self):
        custom_resilience = {
            'retry': {
                'max_retries': 5,
                'base_delay': 2.0,
                'max_delay': 60.0
            },
            'circuit_breaker': {
                'failure_threshold': 10,
                'recovery_timeout': 120.0,
                'window_size': 20
            }
        }
        config_data = {'resilience': custom_resilience}
        
        with patch('builtins.open', mock_open(read_data=yaml.dump(config_data))):
            with patch('core.config.Path.exists', return_value=True):
                config = Config('test_config.yaml')
                
                assert config.resilience == custom_resilience
    
    def test_device_configuration(self):
        config_data = {'device': 'cuda'}
        
        with patch('builtins.open', mock_open(read_data=yaml.dump(config_data))):
            with patch('core.config.Path.exists', return_value=True):
                config = Config('test_config.yaml')
                
                assert config.device == 'cuda'
    
    def test_batch_size_configuration(self):
        config_data = {
            'cpu_batch_size': 16,
            'gpu_batch_size': 64
        }
        
        with patch('builtins.open', mock_open(read_data=yaml.dump(config_data))):
            with patch('core.config.Path.exists', return_value=True):
                config = Config('test_config.yaml')
                
                assert config.cpu_batch_size == 16
                assert config.gpu_batch_size == 64
    
    def test_chunk_configuration(self):
        config_data = {
            'chunk_size': 1024,
            'chunk_overlap': 0.3
        }
        
        with patch('builtins.open', mock_open(read_data=yaml.dump(config_data))):
            with patch('core.config.Path.exists', return_value=True):
                config = Config('test_config.yaml')
                
                assert config.chunk_size == 1024
                assert config.chunk_overlap == 0.3
    
    def test_api_configuration(self):
        config_data = {
            'embedding_api_url': 'http://localhost:8000',
            'embedding_type': 'api',
            'llm_api_url': 'http://localhost:11434',
            'llm_type': 'api'
        }
        
        with patch('builtins.open', mock_open(read_data=yaml.dump(config_data))):
            with patch('core.config.Path.exists', return_value=True):
                config = Config('test_config.yaml')
                
                assert config.embedding_api_url == 'http://localhost:8000'
                assert config.embedding_type == 'api'
                assert config.llm_api_url == 'http://localhost:11434'
                assert config.llm_type == 'api'
    
    def test_budget_configuration(self):
        config_data = {'monthly_budget_limit': 500.0}
        
        with patch('builtins.open', mock_open(read_data=yaml.dump(config_data))):
            with patch('core.config.Path.exists', return_value=True):
                config = Config('test_config.yaml')
                
                assert config.monthly_budget_limit == 500.0
    
    def test_models_configuration(self):
        models_config = {
            'cheap_model': {
                'type': 'api',
                'model_name': 'llama2'
            },
            'strong_model': {
                'type': 'openai',
                'model_name': 'gpt-4'
            }
        }
        config_data = {'models': models_config}
        
        with patch('builtins.open', mock_open(read_data=yaml.dump(config_data))):
            with patch('core.config.Path.exists', return_value=True):
                config = Config('test_config.yaml')
                
                assert config.models == models_config
    
    def test_redis_disabled_by_default(self):
        with patch.dict('os.environ', {}, clear=True):
            with patch('core.config.Path.exists', return_value=False):
                config = Config()
                
                assert config.redis_enabled is False
    
    def test_rate_limit_enabled_by_default(self):
        with patch.dict('os.environ', {}, clear=True):
            with patch('core.config.Path.exists', return_value=False):
                config = Config()
                
                assert config.rate_limit_enabled is True
