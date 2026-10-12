import pytest
from unittest.mock import Mock, patch
from core.orchestrator import Orchestrator

@pytest.mark.unit
class TestOrchestrator:
    def test_execute_basic_flow(self, mock_retriever, mock_llm_router, mock_evaluator):
        orchestrator = Orchestrator(
            mock_retriever,
            mock_llm_router,
            mock_evaluator,
            critic_threshold=0.6,
            retry_enabled=False
        )
        
        result = orchestrator.execute("test query", top_k=5)
        
        assert 'answer' in result
        assert 'sources' in result
        assert 'evaluation' in result
        assert 'trace' in result
        assert len(result['trace']) > 0
    
    def test_execute_with_empty_query(self, mock_retriever, mock_llm_router, mock_evaluator):
        orchestrator = Orchestrator(
            mock_retriever,
            mock_llm_router,
            mock_evaluator
        )
        
        result = orchestrator.execute("", top_k=5)
        assert result is not None
    
    def test_execute_with_budget_exceeded(self, mock_retriever, mock_llm_router, mock_evaluator):
        orchestrator = Orchestrator(
            mock_retriever,
            mock_llm_router,
            mock_evaluator,
            budget_limit=0.01
        )
        orchestrator.token_tracker.cumulative_cost = 100.0
        
        result = orchestrator.execute("test query", top_k=5)
        assert result is not None
    
    def test_trace_recording(self, mock_retriever, mock_llm_router, mock_evaluator):
        orchestrator = Orchestrator(
            mock_retriever,
            mock_llm_router,
            mock_evaluator
        )
        
        result = orchestrator.execute("test query", top_k=5)
        
        assert len(result['trace']) > 0
        for step in result['trace']:
            assert 'step' in step
            assert 'agent' in step
            assert 'latency' in step
