import pytest
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient

@pytest.fixture
def test_client():
    with patch('api.routes.HybridRetrieverAsync'):
        with patch('api.routes.LLMRouterAsync'):
            with patch('api.routes.Evaluator'):
                with patch('api.routes.OrchestratorAsync'):
                    from main import app
                    return TestClient(app)

def test_query_endpoint_basic(test_client):
    with patch('api.routes.orchestrator') as mock_orch:
        mock_orch.execute = AsyncMock(return_value={
            'answer': 'Test answer',
            'sources': [],
            'evaluation': {'confidence_score': 0.9},
            'trace': [],
            'routing': {}
        })
        
        response = test_client.post('/api/v1/query', json={'query': 'test'})
        assert response.status_code == 200

def test_query_endpoint_with_top_k(test_client):
    with patch('api.routes.orchestrator') as mock_orch:
        mock_orch.execute = AsyncMock(return_value={
            'answer': 'Test',
            'sources': [],
            'evaluation': {},
            'trace': [],
            'routing': {}
        })
        
        response = test_client.post('/api/v1/query', json={'query': 'test', 'top_k': 10})
        assert response.status_code == 200

def test_query_endpoint_empty_query(test_client):
    response = test_client.post('/api/v1/query', json={'query': ''})
    assert response.status_code in [200, 400, 422]

def test_query_endpoint_missing_query(test_client):
    response = test_client.post('/api/v1/query', json={})
    assert response.status_code == 422
