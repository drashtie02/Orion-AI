import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock, AsyncMock
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

@pytest.mark.api
class TestQueryAPI:
    @patch('api.routes.initialize_components')
    @patch('api.routes.retriever')
    @patch('api.routes.orchestrator')
    def test_query_endpoint_success(self, mock_orchestrator, mock_retriever, mock_init):
        mock_orchestrator.execute = AsyncMock(return_value={
            'answer': 'Test answer',
            'sources': [],
            'evaluation': {'confidence_score': 0.9},
            'trace': [],
            'routing': {}
        })
        
        from main import app
        client = TestClient(app)
        
        response = client.post(
            "/api/v1/query",
            json={"query": "test query", "top_k": 5}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert 'answer' in data
        assert 'request_id' in data
        assert 'X-Request-ID' in response.headers
    
    @patch('api.routes.initialize_components')
    @patch('api.routes.orchestrator')
    def test_query_endpoint_empty_query(self, mock_orchestrator, mock_init):
        mock_orchestrator.execute = AsyncMock(return_value={
            'answer': 'Empty',
            'sources': [],
            'evaluation': {},
            'trace': [],
            'routing': {}
        })
        
        from main import app
        client = TestClient(app)
        
        response = client.post(
            "/api/v1/query",
            json={"query": "", "top_k": 5}
        )
        
        assert response.status_code in [200, 422]
    
    @patch('api.routes.initialize_components')
    def test_query_endpoint_invalid_payload(self, mock_init):
        from main import app
        client = TestClient(app)
        
        response = client.post(
            "/api/v1/query",
            json={"invalid": "payload"}
        )
        
        assert response.status_code == 422
    
    def test_health_endpoint(self):
        from main import app
        client = TestClient(app)
        
        response = client.get("/health")
        assert response.status_code == 200
    
    @patch('api.routes.initialize_components')
    @patch('api.routes.cache_manager')
    @patch('api.routes.orchestrator')
    def test_query_with_cache_hit(self, mock_orchestrator, mock_cache, mock_init):
        mock_cache.get = AsyncMock(return_value={
            'answer': 'Cached answer',
            'sources': [],
            'evaluation': {},
            'trace': [],
            'routing': {}
        })
        
        from main import app
        client = TestClient(app)
        
        response = client.post(
            "/api/v1/query",
            json={"query": "test query", "top_k": 5}
        )
        
        assert response.status_code == 200
