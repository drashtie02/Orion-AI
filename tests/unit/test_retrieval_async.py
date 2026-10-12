import pytest
from unittest.mock import Mock, AsyncMock, patch
import numpy as np
from retrieval.hybrid_async import HybridRetrieverAsync
from retrieval.vector_store import VectorStore
from retrieval.bm25 import BM25Index

@pytest.fixture
def mock_chunks():
    return [
        {'chunk_id': 'chunk_0', 'text': 'Machine learning', 'source_path': 'test.txt'},
        {'chunk_id': 'chunk_1', 'text': 'Deep learning', 'source_path': 'test.txt'}
    ]

class TestHybridRetrieverAsync:
    @pytest.mark.asyncio
    async def test_initialization(self):
        with patch('retrieval.hybrid_async.VectorStore'):
            with patch('retrieval.hybrid_async.BM25Index'):
                retriever = HybridRetrieverAsync(alpha=0.5)
                
                assert retriever.alpha == 0.5
                assert retriever.vector_store is not None
                assert retriever.bm25_index is not None
    
    @pytest.mark.asyncio
    async def test_search(self, mock_chunks):
        with patch('retrieval.hybrid_async.VectorStore') as mock_vs:
            with patch('retrieval.hybrid_async.BM25Index') as mock_bm25:
                mock_vs_instance = Mock()
                mock_vs_instance.search = Mock(return_value=[
                    (mock_chunks[0], 0.9),
                    (mock_chunks[1], 0.8)
                ])
                mock_vs.return_value = mock_vs_instance
                
                mock_bm25_instance = Mock()
                mock_bm25_instance.search = Mock(return_value=[
                    (mock_chunks[0], 0.85),
                    (mock_chunks[1], 0.75)
                ])
                mock_bm25.return_value = mock_bm25_instance
                
                retriever = HybridRetrieverAsync(alpha=0.5)
                results = await retriever.search("test query", top_k=2)
                
                assert len(results) <= 2
                assert all('hybrid_score' in r for r in results)
    
    @pytest.mark.asyncio
    async def test_search_empty_results(self):
        with patch('retrieval.hybrid_async.VectorStore') as mock_vs:
            with patch('retrieval.hybrid_async.BM25Index') as mock_bm25:
                mock_vs_instance = Mock()
                mock_vs_instance.search = Mock(return_value=[])
                mock_vs.return_value = mock_vs_instance
                
                mock_bm25_instance = Mock()
                mock_bm25_instance.search = Mock(return_value=[])
                mock_bm25.return_value = mock_bm25_instance
                
                retriever = HybridRetrieverAsync(alpha=0.5)
                results = await retriever.search("test query", top_k=5)
                
                assert len(results) == 0
    
    def test_set_alpha(self):
        with patch('retrieval.hybrid_async.VectorStore'):
            with patch('retrieval.hybrid_async.BM25Index'):
                retriever = HybridRetrieverAsync(alpha=0.5)
                retriever.set_alpha(0.7)
                
                assert retriever.alpha == 0.7
    
    def test_normalize_scores(self):
        with patch('retrieval.hybrid_async.VectorStore'):
            with patch('retrieval.hybrid_async.BM25Index'):
                retriever = HybridRetrieverAsync()
                
                scores = [0.5, 0.7, 0.9]
                normalized = retriever._normalize_scores(scores)
                
                assert len(normalized) == 3
                assert min(normalized) == 0.0
                assert max(normalized) == 1.0
    
    def test_normalize_scores_empty(self):
        with patch('retrieval.hybrid_async.VectorStore'):
            with patch('retrieval.hybrid_async.BM25Index'):
                retriever = HybridRetrieverAsync()
                
                normalized = retriever._normalize_scores([])
                
                assert normalized == []
    
    def test_normalize_scores_uniform(self):
        with patch('retrieval.hybrid_async.VectorStore'):
            with patch('retrieval.hybrid_async.BM25Index'):
                retriever = HybridRetrieverAsync()
                
                normalized = retriever._normalize_scores([0.5, 0.5, 0.5])
                
                assert all(s == 0.0 for s in normalized)
    
    def test_shutdown(self):
        with patch('retrieval.hybrid_async.VectorStore'):
            with patch('retrieval.hybrid_async.BM25Index'):
                retriever = HybridRetrieverAsync()
                retriever.shutdown()
                
                assert retriever._executor is not None

class TestVectorStore:
    def test_initialization_with_local_model(self):
        with patch('retrieval.vector_store.config') as mock_config:
            mock_config.embedding_type = 'local'
            mock_config.embedding_model = 'test-model'
            
            with patch('retrieval.vector_store.SentenceTransformer') as mock_st:
                mock_model = Mock()
                mock_model.get_sentence_embedding_dimension.return_value = 384
                mock_st.return_value = mock_model
                
                with patch('retrieval.vector_store.device_manager') as mock_dm:
                    mock_dm.get_device.return_value = 'cpu'
                    mock_dm.is_cuda.return_value = False
                    
                    store = VectorStore()
                    
                    assert store.model is not None
                    assert store.dimension == 384
    
    def test_initialization_with_api_model(self):
        with patch('retrieval.vector_store.config') as mock_config:
            mock_config.embedding_type = 'api'
            mock_config.embedding_api_url = 'http://localhost:8000'
            mock_config.embedding_model = 'test-model'
            
            with patch('retrieval.vector_store.APIEmbeddingModel') as mock_api:
                mock_model = Mock()
                mock_model.get_sentence_embedding_dimension.return_value = 384
                mock_api.return_value = mock_model
                
                store = VectorStore()
                
                assert store.model is not None
    
    def test_build_index(self, mock_chunks):
        with patch('retrieval.vector_store.config') as mock_config:
            mock_config.embedding_type = 'local'
            mock_config.embedding_model = 'test-model'
            
            with patch('retrieval.vector_store.SentenceTransformer') as mock_st:
                mock_model = Mock()
                mock_model.get_sentence_embedding_dimension.return_value = 384
                mock_model.encode = Mock(return_value=np.random.rand(2, 384))
                mock_st.return_value = mock_model
                
                with patch('retrieval.vector_store.device_manager') as mock_dm:
                    mock_dm.get_device.return_value = 'cpu'
                    mock_dm.is_cuda.return_value = False
                    
                    store = VectorStore()
                    store.build_index(mock_chunks)
                    
                    assert store.index is not None
                    assert len(store.metadata) == 2
    
    def test_search(self, mock_chunks):
        with patch('retrieval.vector_store.config') as mock_config:
            mock_config.embedding_type = 'local'
            mock_config.embedding_model = 'test-model'
            
            with patch('retrieval.vector_store.SentenceTransformer') as mock_st:
                mock_model = Mock()
                mock_model.get_sentence_embedding_dimension.return_value = 384
                mock_model.encode = Mock(return_value=np.random.rand(1, 384))
                mock_st.return_value = mock_model
                
                with patch('retrieval.vector_store.device_manager') as mock_dm:
                    mock_dm.get_device.return_value = 'cpu'
                    mock_dm.is_cuda.return_value = False
                    
                    store = VectorStore()
                    store.metadata = mock_chunks
                    
                    with patch.object(store, 'index') as mock_index:
                        mock_index.search = Mock(return_value=(
                            np.array([[0.9, 0.8]]),
                            np.array([[0, 1]])
                        ))
                        
                        results = store.search("test query", top_k=2)
                        
                        assert len(results) == 2
    
    def test_embed_query(self):
        with patch('retrieval.vector_store.config') as mock_config:
            mock_config.embedding_type = 'local'
            mock_config.embedding_model = 'test-model'
            
            with patch('retrieval.vector_store.SentenceTransformer') as mock_st:
                mock_model = Mock()
                mock_model.get_sentence_embedding_dimension.return_value = 384
                mock_model.encode = Mock(return_value=np.random.rand(1, 384))
                mock_st.return_value = mock_model
                
                with patch('retrieval.vector_store.device_manager') as mock_dm:
                    mock_dm.get_device.return_value = 'cpu'
                    mock_dm.is_cuda.return_value = False
                    
                    store = VectorStore()
                    embedding = store.embed_query("test query")
                    
                    assert embedding is not None
                    assert len(embedding) == 384
