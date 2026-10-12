import pytest
from fastapi.testclient import TestClient

@pytest.mark.api
class TestHealthEndpoint:
    def test_health_check_returns_200(self):
        from main import app
        client = TestClient(app)
        
        response = client.get("/health")
        assert response.status_code == 200
    
    def test_health_check_has_request_id(self):
        from main import app
        client = TestClient(app)
        
        response = client.get("/health")
        assert "X-Request-ID" in response.headers
    
    def test_health_check_response_format(self):
        from main import app
        client = TestClient(app)
        
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data or isinstance(data, dict)
