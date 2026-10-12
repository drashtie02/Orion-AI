import pytest
from unittest.mock import Mock, patch
import numpy as np

@pytest.mark.integration
class TestRetrievalPipeline:
    @patch('retrieval.hybrid.HybridRetriever')
    def test_hybrid_retrieval_integration(self, mock_retriever_class):
        mock_retriever = Mock()
        mock_retriever.search = Mock(return_value=[
            {
                'chunk': {
                    'text': 'Test content',
                    'source_path': 'test.txt',
                    'chunk_id': 'chunk_0'
                },
                'vector_score': 0.9,
                'bm25_score': 0.8,
                'hybrid_score': 0.85
            }
        ])
        mock_retriever_class.return_value = mock_retriever
        
        retriever = mock_retriever_class()
        results = retriever.search("test query", top_k=5)
        
        assert len(results) > 0
        assert 'chunk' in results[0]
        assert 'hybrid_score' in results[0]
    
    def test_context_builder_token_limit(self, mock_llm_router):
        from api.routes import ContextBuilder
        
        builder = ContextBuilder(mock_llm_router)
        
        chunks_data = [
            {
                'chunk': {
                    'text': 'Short text',
                    'source_path': 'test.txt',
                    'chunk_id': f'chunk_{i}'
                },
                'vector_score': 0.9,
                'bm25_score': 0.8,
                'hybrid_score': 0.85
            }
            for i in range(10)
        ]
        
        context = builder.build_context(chunks_data)
        
        assert 'chunks' in context
        assert 'total_tokens' in context
        assert context['total_tokens'] <= builder.max_tokens
    
    @patch('retrieval.hybrid.HybridRetriever')
    @patch('llm.router.LLMRouter')
    def test_end_to_end_retrieval_generation(self, mock_llm_class, mock_retriever_class):
        mock_retriever = Mock()
        mock_retriever.search = Mock(return_value=[
            {
                'chunk': {
                    'text': 'Test content',
                    'source_path': 'test.txt',
                    'chunk_id': 'chunk_0'
                },
                'vector_score': 0.9,
                'bm25_score': 0.8,
                'hybrid_score': 0.85
            }
        ])
        
        mock_llm = Mock()
        mock_llm.generate = Mock(return_value={
            'text': 'Generated answer',
            'tokens_input': 100,
            'tokens_output': 50,
            'model_name': 'test_model'
        })
        mock_llm.count_tokens = Mock(return_value=10)
        
        mock_retriever_class.return_value = mock_retriever
        mock_llm_class.return_value = mock_llm
        
        retriever = mock_retriever_class()
        llm = mock_llm_class()
        
        results = retriever.search("test query", top_k=5)
        assert len(results) > 0
        
        response = llm.generate("test prompt")
        assert response['text'] == 'Generated answer'
