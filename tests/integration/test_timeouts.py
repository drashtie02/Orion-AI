import pytest
from unittest.mock import Mock, patch
import time

@pytest.mark.integration
class TestTimeoutAndExceptions:
    def test_llm_timeout_handling(self, mock_retriever, mock_evaluator):
        def slow_generate(*args, **kwargs):
            time.sleep(0.2)
            return {
                'text': 'Slow response',
                'tokens_input': 100,
                'tokens_output': 50,
                'model_name': 'test_model'
            }
        
        mock_llm = Mock()
        mock_llm.generate = Mock(side_effect=slow_generate)
        
        from core.orchestrator import Orchestrator
        
        orchestrator = Orchestrator(
            mock_retriever,
            mock_llm,
            mock_evaluator
        )
        
        result = orchestrator.execute("test query", top_k=5)
        assert result is not None
    
    def test_redis_connection_failure_graceful(self):
        with patch('core.cache.aioredis.Redis', side_effect=Exception("Connection failed")):
            with patch.dict('os.environ', {'REDIS_ENABLED': 'true'}):
                from core.cache import CacheManager
                
                cache = CacheManager()
                assert cache.enabled is False
    
    def test_rate_limit_redis_failure_fallback(self):
        with patch('core.middleware.rate_limit.aioredis.Redis', side_effect=Exception("Redis down")):
            with patch.dict('os.environ', {'RATE_LIMIT_ENABLED': 'true'}):
                from core.middleware.rate_limit import RateLimitMiddleware
                from fastapi import FastAPI
                
                app = FastAPI()
                middleware = RateLimitMiddleware(app)
                
                assert middleware.enabled is False
    
    def test_exception_in_evaluation_does_not_crash(self, mock_retriever, mock_llm_router):
        mock_evaluator = Mock()
        mock_evaluator.evaluate = Mock(side_effect=Exception("Evaluation error"))
        
        from core.orchestrator import Orchestrator
        
        orchestrator = Orchestrator(
            mock_retriever,
            mock_llm_router,
            mock_evaluator
        )
        
        result = orchestrator.execute("test query", top_k=5)
        assert result is not None
        assert 'answer' in result
    
    def test_none_query_handling(self, mock_retriever, mock_llm_router, mock_evaluator):
        from core.orchestrator import Orchestrator
        
        orchestrator = Orchestrator(
            mock_retriever,
            mock_llm_router,
            mock_evaluator
        )
        
        result = orchestrator.execute(None, top_k=5)
        assert result is not None
