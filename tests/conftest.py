import pytest
from unittest.mock import Mock, AsyncMock
from fastapi.testclient import TestClient

@pytest.fixture
def mock_llm_response():
    return {
        'text': 'Test answer',
        'tokens_input': 100,
        'tokens_output': 50,
        'model_name': 'test_model'
    }

@pytest.fixture
def mock_retriever():
    retriever = Mock()
    retriever.search = Mock(return_value=[
        {
            'chunk': {
                'text': 'Test chunk',
                'source_path': 'test.txt',
                'chunk_id': 'chunk_0'
            },
            'vector_score': 0.9,
            'bm25_score': 0.8,
            'hybrid_score': 0.85
        }
    ])
    return retriever

@pytest.fixture
def mock_llm_router(mock_llm_response):
    router = Mock()
    router.generate = Mock(return_value=mock_llm_response)
    router.count_tokens = Mock(return_value=10)
    router.model_name = 'test_model'
    return router

@pytest.fixture
def mock_evaluator():
    evaluator = Mock()
    evaluator.evaluate = Mock(return_value={
        'faithfulness': {'faithfulness_score': 0.9},
        'relevance': {'relevance_score': 0.85},
        'hallucination': {'hallucination_risk': 0.1},
        'confidence_score': 0.88
    })
    return evaluator

@pytest.fixture
def mock_redis():
    redis_mock = AsyncMock()
    redis_mock.get = AsyncMock(return_value=None)
    redis_mock.setex = AsyncMock(return_value=True)
    redis_mock.incr = AsyncMock(return_value=1)
    redis_mock.ttl = AsyncMock(return_value=60)
    redis_mock.close = AsyncMock()
    return redis_mock

@pytest.fixture
def mock_embedding_model():
    import numpy as np
    model = Mock()
    model.encode = Mock(return_value=np.array([[0.1, 0.2, 0.3]]))
    model.get_sentence_embedding_dimension = Mock(return_value=384)
    return model

@pytest.fixture
def sample_chunks():
    return [
        {
            'chunk_id': 'chunk_0',
            'text': 'Machine learning is a subset of AI',
            'source_path': 'test.txt'
        },
        {
            'chunk_id': 'chunk_1',
            'text': 'Deep learning uses neural networks',
            'source_path': 'test.txt'
        }
    ]
