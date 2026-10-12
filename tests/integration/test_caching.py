import pytest
from unittest.mock import patch, AsyncMock, Mock

@pytest.mark.integration
@pytest.mark.asyncio
class TestCachingIntegration:
    async def test_query_caching_flow(self, mock_redis):
        with patch('core.cache.aioredis.Redis', return_value=mock_redis):
            with patch.dict('os.environ', {'REDIS_ENABLED': 'true'}):
                from core.cache import CacheManager
                
                cache = CacheManager()
                cache.client = mock_redis
                cache.enabled = True
                
                mock_redis.get.return_value = None
                result = await cache.get('query', 'test_key')
                assert result is None
                
                await cache.set('query', 'test_key', {'answer': 'cached'})
                mock_redis.setex.assert_called_once()
    
    async def test_retrieval_caching_flow(self, mock_redis):
        with patch('core.cache.aioredis.Redis', return_value=mock_redis):
            with patch.dict('os.environ', {'REDIS_ENABLED': 'true'}):
                from core.cache import CacheManager
                
                cache = CacheManager()
                cache.client = mock_redis
                cache.enabled = True
                
                retrieval_result = [
                    {
                        'chunk': {'text': 'test', 'chunk_id': 'c1'},
                        'hybrid_score': 0.9
                    }
                ]
                
                await cache.set('retrieval', 'query_key', retrieval_result)
                mock_redis.setex.assert_called()
    
    async def test_cache_ttl_configuration(self, mock_redis):
        with patch('core.cache.aioredis.Redis', return_value=mock_redis):
            with patch.dict('os.environ', {
                'REDIS_ENABLED': 'true',
                'CACHE_TTL': '7200'
            }):
                from core.cache import CacheManager
                
                cache = CacheManager()
                cache.client = mock_redis
                cache.enabled = True
                
                assert cache.ttl == 7200
                
                await cache.set('test', 'key', {'data': 'value'})
                
                call_args = mock_redis.setex.call_args
                assert call_args[0][1] == 7200
