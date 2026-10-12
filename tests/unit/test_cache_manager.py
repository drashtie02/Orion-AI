import pytest
from unittest.mock import Mock, AsyncMock, patch
from core.cache import CacheManager

@pytest.mark.asyncio
async def test_cache_manager_disabled_by_default():
    with patch.dict('os.environ', {}, clear=True):
        cache = CacheManager()
        assert cache.enabled is False
        assert cache.client is None

@pytest.mark.asyncio
async def test_cache_manager_enabled():
    with patch.dict('os.environ', {'REDIS_ENABLED': 'true'}):
        with patch('core.cache.aioredis.Redis') as mock_redis:
            mock_client = AsyncMock()
            mock_redis.return_value = mock_client
            
            cache = CacheManager()
            assert cache.enabled is True

@pytest.mark.asyncio
async def test_cache_manager_connection_failure():
    with patch.dict('os.environ', {'REDIS_ENABLED': 'true'}):
        with patch('core.cache.ConnectionPool', side_effect=Exception("Connection failed")):
            cache = CacheManager()
            assert cache.enabled is False

@pytest.mark.asyncio
async def test_get_when_disabled():
    cache = CacheManager()
    cache.enabled = False
    
    result = await cache.get('test', 'key')
    assert result is None

@pytest.mark.asyncio
async def test_get_cache_hit():
    cache = CacheManager()
    cache.enabled = True
    cache.client = AsyncMock()
    cache.client.get = AsyncMock(return_value='{"data": "value"}')
    
    result = await cache.get('test', 'key')
    assert result == {'data': 'value'}

@pytest.mark.asyncio
async def test_get_cache_miss():
    cache = CacheManager()
    cache.enabled = True
    cache.client = AsyncMock()
    cache.client.get = AsyncMock(return_value=None)
    
    result = await cache.get('test', 'key')
    assert result is None

@pytest.mark.asyncio
async def test_get_with_error():
    cache = CacheManager()
    cache.enabled = True
    cache.client = AsyncMock()
    cache.client.get = AsyncMock(side_effect=Exception("Redis error"))
    
    result = await cache.get('test', 'key')
    assert result is None

@pytest.mark.asyncio
async def test_set_when_disabled():
    cache = CacheManager()
    cache.enabled = False
    
    result = await cache.set('test', 'key', {'data': 'value'})
    assert result is False

@pytest.mark.asyncio
async def test_set_success():
    cache = CacheManager()
    cache.enabled = True
    cache.client = AsyncMock()
    cache.client.setex = AsyncMock(return_value=True)
    
    result = await cache.set('test', 'key', {'data': 'value'})
    assert result is True

@pytest.mark.asyncio
async def test_set_with_custom_ttl():
    cache = CacheManager()
    cache.enabled = True
    cache.client = AsyncMock()
    cache.client.setex = AsyncMock(return_value=True)
    
    result = await cache.set('test', 'key', {'data': 'value'}, ttl=7200)
    assert result is True
    cache.client.setex.assert_called_once()

@pytest.mark.asyncio
async def test_set_with_error():
    cache = CacheManager()
    cache.enabled = True
    cache.client = AsyncMock()
    cache.client.setex = AsyncMock(side_effect=Exception("Redis error"))
    
    result = await cache.set('test', 'key', {'data': 'value'})
    assert result is False

@pytest.mark.asyncio
async def test_close():
    cache = CacheManager()
    cache.client = AsyncMock()
    cache.pool = AsyncMock()
    
    await cache.close()
    
    cache.client.close.assert_called_once()
    cache.pool.disconnect.assert_called_once()

@pytest.mark.asyncio
async def test_close_without_client():
    cache = CacheManager()
    cache.client = None
    cache.pool = None
    
    await cache.close()

@pytest.mark.asyncio
async def test_generate_key():
    cache = CacheManager()
    
    key1 = cache._generate_key('prefix', 'data')
    key2 = cache._generate_key('prefix', 'data')
    key3 = cache._generate_key('prefix', 'different')
    
    assert key1 == key2
    assert key1 != key3
    assert key1.startswith('prefix:')

@pytest.mark.asyncio
async def test_custom_redis_config():
    with patch.dict('os.environ', {
        'REDIS_ENABLED': 'true',
        'REDIS_HOST': 'custom-host',
        'REDIS_PORT': '6380',
        'REDIS_DB': '1',
        'CACHE_TTL': '7200'
    }):
        with patch('core.cache.aioredis.Redis'):
            cache = CacheManager()
            
            assert cache.host == 'custom-host'
            assert cache.port == 6380
            assert cache.db == 1
            assert cache.ttl == 7200
