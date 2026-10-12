import pytest
from unittest.mock import patch, Mock, AsyncMock
import asyncio
from concurrent.futures import ThreadPoolExecutor

@pytest.mark.integration
class TestPerformanceAndConcurrency:
    @patch('api.routes.initialize_components')
    @patch('api.routes.orchestrator')
    def test_concurrent_requests(self, mock_orchestrator, mock_init):
        mock_orchestrator.execute = AsyncMock(return_value={
            'answer': 'Test',
            'sources': [],
            'evaluation': {},
            'trace': [],
            'routing': {}
        })
        
        from main import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        
        def make_request():
            return client.post(
                "/api/v1/query",
                json={"query": "test", "top_k": 5}
            )
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [f.result() for f in futures]
        
        assert all(r.status_code == 200 for r in results)
        assert len(set(r.json()['request_id'] for r in results)) == 10
    
    @pytest.mark.asyncio
    async def test_cache_thread_safety(self, mock_redis):
        with patch('core.cache.aioredis.Redis', return_value=mock_redis):
            with patch.dict('os.environ', {'REDIS_ENABLED': 'true'}):
                from core.cache import CacheManager
                
                cache = CacheManager()
                cache.client = mock_redis
                cache.enabled = True
                
                async def cache_operation(i):
                    await cache.set('test', f'key_{i}', {'value': i})
                    return await cache.get('test', f'key_{i}')
                
                results = await asyncio.gather(*[cache_operation(i) for i in range(10)])
                
                assert len(results) == 10
    
    def test_no_global_state_leakage(self):
        from core.middleware.request_id import request_id_var
        
        request_id_var.set('test-id-1')
        assert request_id_var.get() == 'test-id-1'
        
        request_id_var.set('test-id-2')
        assert request_id_var.get() == 'test-id-2'
        assert request_id_var.get() != 'test-id-1'
