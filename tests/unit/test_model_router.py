import pytest
from unittest.mock import Mock
from core.model_router import ModelRouter

@pytest.mark.unit
class TestModelRouter:
    def test_select_initial_model_cheap(self, mock_llm_router):
        router = ModelRouter(mock_llm_router, 'cheap', 'strong', 500, 0.6)
        model = router.select_initial_model('simple', 'low', 100)
        assert model == 'cheap'
    
    def test_select_initial_model_strong(self, mock_llm_router):
        router = ModelRouter(mock_llm_router, 'cheap', 'strong', 500, 0.6)
        model = router.select_initial_model('complex', 'high', 1000)
        assert model == 'strong'
    
    def test_should_escalate_low_confidence(self, mock_llm_router):
        router = ModelRouter(mock_llm_router, 'cheap', 'strong', 500, 0.6)
        should_escalate = router.should_escalate(0.5, 'cheap')
        assert should_escalate is True
    
    def test_should_not_escalate_high_confidence(self, mock_llm_router):
        router = ModelRouter(mock_llm_router, 'cheap', 'strong', 500, 0.6)
        should_escalate = router.should_escalate(0.8, 'cheap')
        assert should_escalate is False
    
    def test_should_not_escalate_already_strong(self, mock_llm_router):
        router = ModelRouter(mock_llm_router, 'cheap', 'strong', 500, 0.6)
        should_escalate = router.should_escalate(0.5, 'strong')
        assert should_escalate is False
    
    def test_record_latency(self, mock_llm_router):
        router = ModelRouter(mock_llm_router, 'cheap', 'strong', 500, 0.6)
        router.record_latency('cheap', 1.5)
        assert 'cheap' in router.latency_history
        assert router.latency_history['cheap'] == [1.5]
