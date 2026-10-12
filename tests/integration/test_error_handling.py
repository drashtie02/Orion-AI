import pytest
from unittest.mock import Mock, patch
from core.orchestrator import Orchestrator

@pytest.mark.integration
class TestErrorHandling:
    def test_orchestrator_handles_retrieval_failure(self, mock_llm_router, mock_evaluator):
        mock_retriever = Mock()
        mock_retriever.search = Mock(side_effect=Exception("Retrieval failed"))
        
        orchestrator = Orchestrator(
            mock_retriever,
            mock_llm_router,
            mock_evaluator
        )
        
        result = orchestrator.execute("test query", top_k=5)
        
        assert result is not None
        assert 'answer' in result
        assert 'trace' in result
    
    def test_orchestrator_handles_llm_failure(self, mock_retriever, mock_evaluator):
        mock_llm = Mock()
        mock_llm.generate = Mock(side_effect=Exception("LLM failed"))
        
        orchestrator = Orchestrator(
            mock_retriever,
            mock_llm,
            mock_evaluator
        )
        
        result = orchestrator.execute("test query", top_k=5)
        
        assert result is not None
    
    def test_orchestrator_handles_evaluation_failure(self, mock_retriever, mock_llm_router):
        mock_evaluator = Mock()
        mock_evaluator.evaluate = Mock(side_effect=Exception("Evaluation failed"))
        
        orchestrator = Orchestrator(
            mock_retriever,
            mock_llm_router,
            mock_evaluator
        )
        
        result = orchestrator.execute("test query", top_k=5)
        
        assert result is not None
        assert 'answer' in result
    
    def test_timeout_handling(self, mock_retriever, mock_llm_router, mock_evaluator):
        import time
        
        def slow_generate(*args, **kwargs):
            time.sleep(0.1)
            return {
                'text': 'Slow answer',
                'tokens_input': 100,
                'tokens_output': 50,
                'model_name': 'test_model'
            }
        
        mock_llm_router.generate = Mock(side_effect=slow_generate)
        
        orchestrator = Orchestrator(
            mock_retriever,
            mock_llm_router,
            mock_evaluator
        )
        
        result = orchestrator.execute("test query", top_k=5)
        assert result is not None
    
    def test_malformed_input_handling(self, mock_retriever, mock_llm_router, mock_evaluator):
        orchestrator = Orchestrator(
            mock_retriever,
            mock_llm_router,
            mock_evaluator
        )
        
        result = orchestrator.execute(None, top_k=5)
        assert result is not None
