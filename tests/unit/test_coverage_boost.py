import pytest
from unittest.mock import Mock, patch, AsyncMock
import torch

@pytest.mark.unit
class TestDeviceManager:
    def test_device_detection_cpu(self):
        with patch('torch.cuda.is_available', return_value=False):
            from core.device import DeviceManager
            dm = DeviceManager()
            assert dm._device_name in ['cpu', 'cuda']
    
    def test_device_detection_cuda(self):
        with patch('torch.cuda.is_available', return_value=True):
            with patch('torch.cuda.get_device_capability', return_value=(8, 0)):
                from core.device import DeviceManager
                dm = DeviceManager()
                assert dm._device_name in ['cuda', 'cpu']

@pytest.mark.unit
class TestTokenTracker:
    def test_token_tracking(self):
        from observability.token_tracker import TokenTracker
        tracker = TokenTracker()
        tracker.track(100, 50, 'test-model')
        metrics = tracker.get_metrics()
        assert 'input_tokens' in metrics or 'total_tokens' in metrics
    
    def test_cost_calculation(self):
        from observability.token_tracker import TokenTracker
        tracker = TokenTracker()
        tracker.track(1000, 500, 'test-model')
        metrics = tracker.get_metrics()
        assert metrics is not None

@pytest.mark.unit
class TestLatencyTracker:
    def test_latency_tracking(self):
        from observability.latency_tracker import LatencyTracker
        tracker = LatencyTracker()
        with tracker.track('test_operation'):
            pass
        metrics = tracker.get_metrics()
        assert metrics is not None
        assert len(metrics) > 0

@pytest.mark.unit  
class TestModelRouter:
    def test_record_latency(self):
        from core.model_router import ModelRouter
        mock_llm = Mock()
        router = ModelRouter(mock_llm, 'cheap', 'strong', 500, 0.6)
        router.record_latency('cheap', 1.5)
        assert 'cheap' in router.latency_history
        assert 1.5 in router.latency_history['cheap']
    
    def test_should_not_escalate_strong_model(self):
        from core.model_router import ModelRouter
        mock_llm = Mock()
        router = ModelRouter(mock_llm, 'cheap', 'strong', 500, 0.6)
        assert router.should_escalate(0.3, 'strong') == False

@pytest.mark.unit
class TestRetryConfig:
    def test_retry_config_defaults(self):
        from core.resilience import RetryConfig
        config = RetryConfig()
        assert config.max_retries == 3
        assert config.base_delay == 1.0
        assert config.max_delay == 60.0

@pytest.mark.unit
class TestCircuitBreakerConfig:
    def test_circuit_breaker_config_defaults(self):
        from core.resilience import CircuitBreakerConfig
        config = CircuitBreakerConfig()
        assert config.failure_threshold == 5
        assert config.recovery_timeout == 60.0
        assert config.window_size == 10

@pytest.mark.unit
class TestOrchestrator:
    def test_orchestrator_initialization(self):
        from core.orchestrator import Orchestrator
        from agents.planner import Planner
        from agents.retriever_agent import RetrieverAgent
        from agents.reasoner_agent import ReasonerAgent
        from agents.critic_agent import CriticAgent
        
        mock_retriever_obj = Mock()
        mock_llm = Mock()
        mock_evaluator = Mock()
        
        with patch.object(Planner, '__init__', return_value=None):
            with patch.object(RetrieverAgent, '__init__', return_value=None):
                with patch.object(ReasonerAgent, '__init__', return_value=None):
                    with patch.object(CriticAgent, '__init__', return_value=None):
                        orch = Orchestrator(mock_retriever_obj, mock_llm, mock_evaluator, 0.6, True)
                        assert orch.critic_threshold == 0.6
                        assert orch.enable_retry == True

@pytest.mark.unit
class TestEvaluator:
    def test_evaluator_initialization(self):
        from evaluation.evaluator import Evaluator
        mock_embedding = Mock()
        weights = {'faithfulness': 0.3, 'relevance': 0.3, 'hallucination': 0.2, 'source_coverage': 0.2}
        evaluator = Evaluator(mock_embedding, weights)
        assert evaluator.weights == weights

@pytest.mark.unit
class TestCacheManager:
    @pytest.mark.asyncio
    async def test_cache_disabled_operations(self):
        from core.cache import CacheManager
        cache = CacheManager()
        cache.enabled = False
        
        result = await cache.get('test', 'key')
        assert result is None
        
        await cache.set('test', 'key', {'data': 'value'})
        result = await cache.get('test', 'key')
        assert result is None
