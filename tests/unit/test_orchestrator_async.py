import pytest
from unittest.mock import Mock, AsyncMock, patch
from core.orchestrator_async import OrchestratorAsync

@pytest.fixture
def async_mock_retriever():
    retriever = Mock()
    retriever.search = AsyncMock(return_value=[
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
def async_mock_llm_router():
    router = Mock()
    router.generate = AsyncMock(return_value={
        'text': 'Test answer',
        'tokens_input': 100,
        'tokens_output': 50,
        'model_name': 'test_model'
    })
    return router

@pytest.fixture
def async_mock_evaluator():
    evaluator = Mock()
    evaluator.evaluate = Mock(return_value={
        'faithfulness': {'faithfulness_score': 0.9},
        'relevance': {'relevance_score': 0.85},
        'hallucination': {'hallucination_risk': 0.1},
        'confidence_score': 0.88
    })
    return evaluator

@pytest.mark.asyncio
async def test_execute_basic_flow(async_mock_retriever, async_mock_llm_router, async_mock_evaluator):
    orchestrator = OrchestratorAsync(
        async_mock_retriever,
        async_mock_llm_router,
        async_mock_evaluator,
        critic_threshold=0.6,
        retry_enabled=False
    )
    
    result = await orchestrator.execute("test query", top_k=5)
    
    assert 'answer' in result
    assert 'sources' in result
    assert 'evaluation' in result
    assert 'trace' in result
    assert len(result['trace']) > 0

@pytest.mark.asyncio
async def test_execute_with_model_router(async_mock_retriever, async_mock_llm_router, async_mock_evaluator):
    mock_model_router = Mock()
    mock_model_router.cheap_model = 'cheap_model'
    
    orchestrator = OrchestratorAsync(
        async_mock_retriever,
        async_mock_llm_router,
        async_mock_evaluator,
        model_router=mock_model_router
    )
    
    result = await orchestrator.execute("test query", top_k=5)
    
    assert result['routing']['initial_model'] == 'cheap_model'
    assert result['routing']['final_model'] == 'test_model'

@pytest.mark.asyncio
async def test_execute_with_empty_retrieval(async_mock_retriever, async_mock_llm_router, async_mock_evaluator):
    async_mock_retriever.search = AsyncMock(return_value=[])
    
    orchestrator = OrchestratorAsync(
        async_mock_retriever,
        async_mock_llm_router,
        async_mock_evaluator
    )
    
    result = await orchestrator.execute("test query", top_k=5)
    
    assert result['answer'] == 'Test answer'
    assert len(result['sources']) == 0

@pytest.mark.asyncio
async def test_execute_with_llm_failure(async_mock_retriever, async_mock_llm_router, async_mock_evaluator):
    async_mock_llm_router.generate = AsyncMock(side_effect=Exception("LLM error"))
    
    orchestrator = OrchestratorAsync(
        async_mock_retriever,
        async_mock_llm_router,
        async_mock_evaluator
    )
    
    result = await orchestrator.execute("test query", top_k=5)
    
    assert result['answer'] == 'Error processing query'
    assert len(result['trace']) > 0
    assert result['trace'][-1]['step'] == 'error'

@pytest.mark.asyncio
async def test_execute_with_retrieval_failure(async_mock_retriever, async_mock_llm_router, async_mock_evaluator):
    async_mock_retriever.search = AsyncMock(side_effect=Exception("Retrieval error"))
    
    orchestrator = OrchestratorAsync(
        async_mock_retriever,
        async_mock_llm_router,
        async_mock_evaluator
    )
    
    result = await orchestrator.execute("test query", top_k=5)
    
    assert result['answer'] == 'Error processing query'
    assert result['trace'][-1]['agent'] == 'orchestrator'

@pytest.mark.asyncio
async def test_trace_recording(async_mock_retriever, async_mock_llm_router, async_mock_evaluator):
    orchestrator = OrchestratorAsync(
        async_mock_retriever,
        async_mock_llm_router,
        async_mock_evaluator
    )
    
    result = await orchestrator.execute("test query", top_k=5)
    
    assert len(result['trace']) >= 3
    steps = [t['step'] for t in result['trace']]
    assert 'retrieval' in steps
    assert 'reasoning' in steps
    assert 'evaluation' in steps

@pytest.mark.asyncio
async def test_evaluation_failure_handling(async_mock_retriever, async_mock_llm_router, async_mock_evaluator):
    async_mock_evaluator.evaluate = Mock(side_effect=Exception("Evaluation error"))
    
    orchestrator = OrchestratorAsync(
        async_mock_retriever,
        async_mock_llm_router,
        async_mock_evaluator
    )
    
    result = await orchestrator.execute("test query", top_k=5)
    
    assert result['answer'] == 'Error processing query'

@pytest.mark.asyncio
async def test_budget_tracking(async_mock_retriever, async_mock_llm_router, async_mock_evaluator):
    orchestrator = OrchestratorAsync(
        async_mock_retriever,
        async_mock_llm_router,
        async_mock_evaluator,
        budget_limit=100.0
    )
    
    result = await orchestrator.execute("test query", top_k=5)
    
    assert 'routing' in result
    assert 'estimated_cost' in result['routing']
