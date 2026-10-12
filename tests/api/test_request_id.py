import pytest
from unittest.mock import patch, Mock, AsyncMock
from fastapi.testclient import TestClient

@pytest.mark.api
class TestRequestIDPropagation:
    @patch('api.routes.initialize_components')
    @patch('api.routes.orchestrator')
    def test_request_id_in_response(self, mock_orchestrator, mock_init):
        mock_orchestrator.execute = AsyncMock(return_value={
            'answer': 'Test',
            'sources': [],
            'evaluation': {},
            'trace': [],
            'routing': {}
        })
        
        from main import app
        client = TestClient(app)
        
        response = client.post(
            "/api/v1/query",
            json={"query": "test", "top_k": 5}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert 'request_id' in data
        assert 'X-Request-ID' in response.headers
        assert data['request_id'] == response.headers['X-Request-ID']
    
    @patch('api.routes.initialize_components')
    @patch('api.routes.orchestrator')
    def test_custom_request_id_preserved(self, mock_orchestrator, mock_init):
        mock_orchestrator.execute = AsyncMock(return_value={
            'answer': 'Test',
            'sources': [],
            'evaluation': {},
            'trace': [],
            'routing': {}
        })
        
        from main import app
        client = TestClient(app)
        
        custom_id = "my-custom-id-123"
        response = client.post(
            "/api/v1/query",
            json={"query": "test", "top_k": 5},
            headers={"X-Request-ID": custom_id}
        )
        
        assert response.status_code == 200
        assert response.headers['X-Request-ID'] == custom_id
        assert response.json()['request_id'] == custom_id
