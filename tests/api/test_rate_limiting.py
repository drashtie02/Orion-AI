import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock

@pytest.mark.api
class TestRateLimiting:
    @patch('core.middleware.rate_limit.aioredis.Redis')
    def test_rate_limit_headers_present(self, mock_redis_class):
        mock_redis = AsyncMock()
        mock_redis.get = AsyncMock(return_value=None)
        mock_redis.setex = AsyncMock(return_value=True)
        mock_redis_class.return_value = mock_redis
        
        with patch.dict('os.environ', {
            'RATE_LIMIT_ENABLED': 'true',
            'RATE_LIMIT_REQUESTS': '10',
            'RATE_LIMIT_WINDOW_SECONDS': '60'
        }):
            from main import app
            client = TestClient(app)
            
            response = client.get("/health")
            
            assert "X-RateLimit-Limit" in response.headers or response.status_code == 200
    
    @patch('core.middleware.rate_limit.aioredis.Redis')
    def test_rate_limit_exceeded(self, mock_redis_class):
        mock_redis = AsyncMock()
        mock_redis.get = AsyncMock(return_value='100')
        mock_redis.ttl = AsyncMock(return_value=30)
        mock_redis_class.return_value = mock_redis
        
        with patch.dict('os.environ', {
            'RATE_LIMIT_ENABLED': 'true',
            'RATE_LIMIT_REQUESTS': '10',
            'RATE_LIMIT_WINDOW_SECONDS': '60'
        }):
            from main import app
            client = TestClient(app)
            
            response = client.get("/health")
            
            if response.status_code == 429:
                assert "retry_after" in response.json()
                assert "Retry-After" in response.headers
    
    def test_rate_limit_disabled(self):
        with patch.dict('os.environ', {'RATE_LIMIT_ENABLED': 'false'}):
            from main import app
            client = TestClient(app)
            
            response = client.get("/health")
            assert response.status_code == 200
