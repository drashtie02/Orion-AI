import pytest
from unittest.mock import Mock, AsyncMock, patch
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from core.middleware import RequestIDMiddleware, get_request_id

@pytest.mark.unit
class TestRequestIDMiddleware:
    def test_request_id_generation(self):
        app = FastAPI()
        app.add_middleware(RequestIDMiddleware)
        
        @app.get("/test")
        async def test_route():
            return {"request_id": get_request_id()}
        
        client = TestClient(app)
        response = client.get("/test")
        
        assert response.status_code == 200
        assert "X-Request-ID" in response.headers
        assert response.json()["request_id"] == response.headers["X-Request-ID"]
    
    def test_request_id_from_header(self):
        app = FastAPI()
        app.add_middleware(RequestIDMiddleware)
        
        @app.get("/test")
        async def test_route():
            return {"request_id": get_request_id()}
        
        client = TestClient(app)
        custom_id = "custom-request-id-123"
        response = client.get("/test", headers={"X-Request-ID": custom_id})
        
        assert response.headers["X-Request-ID"] == custom_id
        assert response.json()["request_id"] == custom_id

@pytest.mark.unit
@pytest.mark.asyncio
class TestRateLimitMiddleware:
    async def test_rate_limit_disabled(self):
        with patch.dict('os.environ', {'RATE_LIMIT_ENABLED': 'false'}):
            from core.middleware.rate_limit import RateLimitMiddleware
            
            app = FastAPI()
            middleware = RateLimitMiddleware(app)
            
            assert middleware.enabled is False
    
    async def test_rate_limit_headers(self, mock_redis):
        with patch.dict('os.environ', {
            'RATE_LIMIT_ENABLED': 'true',
            'RATE_LIMIT_REQUESTS': '10',
            'RATE_LIMIT_WINDOW_SECONDS': '60'
        }):
            with patch('core.middleware.rate_limit.aioredis.Redis', return_value=mock_redis):
                from core.middleware.rate_limit import RateLimitMiddleware
                
                app = FastAPI()
                app.add_middleware(RateLimitMiddleware)
                
                @app.get("/test")
                async def test_route():
                    return {"status": "ok"}
                
                client = TestClient(app)
                response = client.get("/test")
                
                assert "X-RateLimit-Limit" in response.headers
                assert "X-RateLimit-Remaining" in response.headers
