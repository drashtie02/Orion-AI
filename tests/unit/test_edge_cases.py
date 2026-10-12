import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient

@pytest.mark.unit
class TestEdgeCases:
    @patch('api.routes.initialize_components')
    @patch('api.routes.orchestrator')
    def test_empty_query_string(self, mock_orchestrator, mock_init):
        mock_orchestrator.execute = AsyncMock(return_value={
            'answer': 'Empty query',
            'sources': [],
            'evaluation': {},
            'trace': []
        })
        
        from main import app
        client = TestClient(app)
        
        response = client.post(
            "/api/v1/query",
            json={"query": "", "top_k": 5}
        )
        
        assert response.status_code in [200, 422]
    
    @patch('api.routes.initialize_components')
    @patch('api.routes.orchestrator')
    def test_very_long_query(self, mock_orchestrator, mock_init):
        mock_orchestrator.execute = AsyncMock(return_value={
            'answer': 'Long query',
            'sources': [],
            'evaluation': {},
            'trace': []
        })
        
        from main import app
        client = TestClient(app)
        
        long_query = "test " * 10000
        response = client.post(
            "/api/v1/query",
            json={"query": long_query, "top_k": 5}
        )
        
        assert response.status_code in [200, 413, 422]
    
    @patch('api.routes.initialize_components')
    @patch('api.routes.orchestrator')
    def test_negative_top_k(self, mock_orchestrator, mock_init):
        mock_orchestrator.execute = AsyncMock(return_value={
            'answer': 'Test',
            'sources': [],
            'evaluation': {},
            'trace': []
        })
        
        from main import app
        client = TestClient(app)
        
        response = client.post(
            "/api/v1/query",
            json={"query": "test", "top_k": -1}
        )
        
        assert response.status_code in [200, 422]
    
    @patch('api.routes.initialize_components')
    @patch('api.routes.orchestrator')
    def test_zero_top_k(self, mock_orchestrator, mock_init):
        mock_orchestrator.execute = AsyncMock(return_value={
            'answer': 'Test',
            'sources': [],
            'evaluation': {},
            'trace': []
        })
        
        from main import app
        client = TestClient(app)
        
        response = client.post(
            "/api/v1/query",
            json={"query": "test", "top_k": 0}
        )
        
        assert response.status_code in [200, 422]
    
    @patch('api.routes.initialize_components')
    def test_missing_required_field(self, mock_init):
        from main import app
        client = TestClient(app)
        
        response = client.post(
            "/api/v1/query",
            json={"top_k": 5}
        )
        
        assert response.status_code == 422
    
    @patch('api.routes.initialize_components')
    def test_malformed_json(self, mock_init):
        from main import app
        client = TestClient(app)
        
        response = client.post(
            "/api/v1/query",
            data="not json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422
    
    def test_special_characters_in_query(self):
        from api.routes import ContextBuilder
        
        mock_router = Mock()
        mock_router.count_tokens = Mock(return_value=10)
        
        builder = ContextBuilder(mock_router)
        
        chunks_data = [
            {
                'chunk': {
                    'text': 'Test with special chars: @#$%^&*()',
                    'source_path': 'test.txt',
                    'chunk_id': 'chunk_0'
                },
                'vector_score': 0.9,
                'bm25_score': 0.8,
                'hybrid_score': 0.85
            }
        ]
        
        context = builder.build_context(chunks_data)
        assert len(context['chunks']) > 0
    
    def test_unicode_in_query(self):
        from api.routes import ContextBuilder
        
        mock_router = Mock()
        mock_router.count_tokens = Mock(return_value=10)
        
        builder = ContextBuilder(mock_router)
        
        chunks_data = [
            {
                'chunk': {
                    'text': 'Test with unicode: 你好世界 🌍',
                    'source_path': 'test.txt',
                    'chunk_id': 'chunk_0'
                },
                'vector_score': 0.9,
                'bm25_score': 0.8,
                'hybrid_score': 0.85
            }
        ]
        
        context = builder.build_context(chunks_data)
        assert len(context['chunks']) > 0
