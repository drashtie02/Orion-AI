import pytest
from unittest.mock import patch
import os

@pytest.mark.unit
class TestConfig:
    def test_config_loads_defaults(self):
        with patch('core.config.Path') as mock_path:
            mock_path.return_value.exists.return_value = False
            from core.config import Config
            
            config = Config()
            assert config.top_k_default == 5
            assert config.retrieval_alpha == 0.5
    
    def test_config_loads_environment_variables(self):
        with patch.dict('os.environ', {
            'REDIS_ENABLED': 'true',
            'REDIS_HOST': 'test-redis',
            'REDIS_PORT': '6380',
            'LOG_LEVEL': 'DEBUG'
        }):
            from core.config import Config
            
            config = Config()
            assert config.redis_enabled is True
            assert config.redis_host == 'test-redis'
            assert config.redis_port == 6380
            assert config.log_level == 'DEBUG'
    
    def test_config_rate_limit_defaults(self):
        with patch.dict('os.environ', {}, clear=True):
            from core.config import Config
            
            config = Config()
            assert config.rate_limit_enabled is True
            assert config.rate_limit_requests == 100
            assert config.rate_limit_window == 60
    
    def test_config_cache_defaults(self):
        with patch.dict('os.environ', {}, clear=True):
            from core.config import Config
            
            config = Config()
            assert config.redis_enabled is False
            assert config.cache_ttl == 3600
