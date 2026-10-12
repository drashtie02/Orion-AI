import pytest
from unittest.mock import patch, AsyncMock
from core.cache import CacheManager

@pytest.mark.unit
@pytest.mark.asyncio
class TestCacheManager:
    async def test_cache_disabled_by_default(self):
        with patch.dict('os.environ', {'REDIS_ENABLED': 'false'}):
            cache = CacheManager()
            assert cache.enabled is False
    
    async def test_cache_get_when_disabled(self):
        with patch.dict('os.environ', {'REDIS_ENABLED': 'false'}):
            cache = CacheManager()
            result = await cache.get('test', 'key')
            assert result is None
    
    async def test_cache_set_when_disabled(self):
        with patch.dict('os.environ', {'REDIS_ENABLED': 'false'}):
            cache = CacheManager()
            result = await cache.set('test', 'key', {'data': 'value'})
            assert result is False
    
    async def test_generate_key(self):
        cache = CacheManager()
        key1 = cache._generate_key('prefix', 'data')
        key2 = cache._generate_key('prefix', 'data')
        assert key1 == key2
        assert key1.startswith('prefix:')
    
    async def test_cache_get_with_mock_redis(self, mock_redis):
        with patch.dict('os.environ', {'REDIS_ENABLED': 'true'}):
            with patch('core.cache.aioredis.Redis', return_value=mock_redis):
                cache = CacheManager()
                cache.client = mock_redis
                cache.enabled = True
                
                mock_redis.get.return_value = '{"result": "cached"}'
                result = await cache.get('test', 'key')
                assert result == {"result": "cached"}
    
    async def test_cache_set_with_mock_redis(self, mock_redis):
        with patch.dict('os.environ', {'REDIS_ENABLED': 'true'}):
            with patch('core.cache.aioredis.Redis', return_value=mock_redis):
                cache = CacheManager()
                cache.client = mock_redis
                cache.enabled = True
                
                result = await cache.set('test', 'key', {'data': 'value'})
                assert result is True
                mock_redis.setex.assert_called_once()
