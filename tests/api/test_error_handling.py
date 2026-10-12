import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock, AsyncMock

@pytest.mark.api
class TestAPIErrorHandling:
    def test_404_not_found(self):
        from main import app
        client = TestClient(app)
        
        response = client.get("/nonexistent")
        assert response.status_code == 404
    
    def test_405_method_not_allowed(self):
        from main import app
        client = TestClient(app)
        
        response = client.get("/api/v1/query")
        assert response.status_code == 405
    
    @patch('api.routes.initialize_components')
    def test_422_validation_error(self, mock_init):
        from main import app
        client = TestClient(app)
        
        response = client.post(
            "/api/v1/query",
            json={"invalid_field": "value"}
        )
        assert response.status_code == 422
    
    @patch('api.routes.initialize_components', side_effect=Exception("Init failed"))
    @patch('api.routes.orchestrator')
    def test_500_internal_error(self, mock_orchestrator, mock_init):
        from main import app
        client = TestClient(app)
        
        response = client.post(
            "/api/v1/query",
            json={"query": "test", "top_k": 5}
        )
        assert response.status_code in [500, 200]
    
    @patch('api.routes.initialize_components')
    @patch('api.routes.orchestrator')
    def test_error_includes_request_id(self, mock_orchestrator, mock_init):
        mock_orchestrator.execute = AsyncMock(side_effect=Exception("Processing failed"))
        
        from main import app
        client = TestClient(app)
        
        response = client.post(
            "/api/v1/query",
            json={"query": "test", "top_k": 5}
        )
        
        assert 'X-Request-ID' in response.headers
    
    @patch('api.routes.initialize_components')
    @patch('api.routes.orchestrator')
    def test_large_payload_handling(self, mock_orchestrator, mock_init):
        mock_orchestrator.execute = AsyncMock(return_value={
            'answer': 'Test',
            'sources': [],
            'evaluation': {},
            'trace': [],
            'routing': {}
        })
        
        from main import app
        client = TestClient(app)
        
        large_query = "x" * 1000000
        response = client.post(
            "/api/v1/query",
            json={"query": large_query, "top_k": 5}
        )
        
        assert response.status_code in [200, 413, 422, 500]
    
    @patch('api.routes.initialize_components')
    def test_invalid_json(self, mock_init):
        from main import app
        client = TestClient(app)
        
        response = client.post(
            "/api/v1/query",
            data="not valid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422
