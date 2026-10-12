import pytest
from unittest.mock import Mock, patch
from observability.token_tracker import TokenTracker
from observability.latency_tracker import LatencyTracker

class TestTokenTracker:
    def test_initialization(self):
        tracker = TokenTracker()
        assert tracker.cumulative_cost >= 0.0
        assert tracker.input_tokens == 0
        assert tracker.output_tokens == 0
    
    def test_track_tokens(self):
        tracker = TokenTracker()
        tracker.track(100, 50, 'test_model', 0.001, 0.002)
        
        assert tracker.input_tokens == 100
        assert tracker.output_tokens == 50
        assert abs(tracker.estimated_cost - 0.0002) < 0.0001
    
    def test_track_multiple_calls(self):
        tracker = TokenTracker()
        tracker.track(100, 50, 'test_model', 0.001, 0.002)
        tracker.track(200, 100, 'test_model', 0.001, 0.002)
        
        assert tracker.input_tokens == 300
        assert tracker.output_tokens == 150
        assert abs(tracker.estimated_cost - 0.0006) < 0.0001
    
    def test_track_with_zero_cost(self):
        tracker = TokenTracker()
        tracker.track(100, 50, 'unknown_model', 0.0, 0.0)
        
        assert tracker.estimated_cost == 0.0
    
    def test_get_metrics(self):
        tracker = TokenTracker()
        tracker.track(100, 50, 'test_model', 0.001, 0.002)
        
        metrics = tracker.get_metrics()
        
        assert metrics['input_tokens'] == 100
        assert metrics['output_tokens'] == 50
        assert abs(metrics['estimated_cost'] - 0.0002) < 0.0001
    
    def test_reset(self):
        tracker = TokenTracker()
        tracker.track(100, 50, 'test_model', 0.001, 0.002)
        tracker.reset()
        
        assert tracker.input_tokens == 0
        assert tracker.output_tokens == 0
        assert tracker.estimated_cost == 0.0
    
    def test_track_with_large_numbers(self):
        tracker = TokenTracker()
        tracker.track(1000000, 500000, 'test_model', 0.001, 0.002)
        
        assert abs(tracker.estimated_cost - 2.0) < 0.1
    
    def test_estimate_cost_gpt35(self):
        tracker = TokenTracker()
        tracker.track(1000, 500, 'gpt-3.5-turbo', 0.0, 0.0)
        
        assert tracker.estimated_cost > 0.0
    
    def test_get_cumulative_cost(self):
        tracker = TokenTracker()
        tracker.track(100, 50, 'test_model', 0.001, 0.002)
        
        cost = tracker.get_cumulative_cost()
        assert cost >= 0.0

class TestLatencyTracker:
    def test_initialization(self):
        tracker = LatencyTracker()
        assert tracker.total_latency == 0.0
        assert tracker.retrieval_latency == 0.0
    
    def test_track_latency(self):
        tracker = LatencyTracker()
        with tracker.track('retrieval'):
            pass
        
        assert tracker.retrieval_latency > 0.0
        assert tracker.total_latency > 0.0
    
    def test_track_multiple_operations(self):
        tracker = LatencyTracker()
        with tracker.track('retrieval'):
            pass
        with tracker.track('llm'):
            pass
        with tracker.track('embedding'):
            pass
        
        assert tracker.retrieval_latency > 0.0
        assert tracker.llm_latency > 0.0
        assert tracker.embedding_latency > 0.0
    
    def test_get_metrics(self):
        tracker = LatencyTracker()
        with tracker.track('retrieval'):
            pass
        
        metrics = tracker.get_metrics()
        
        assert 'retrieval_latency' in metrics
        assert 'llm_latency' in metrics
        assert 'total_latency' in metrics
    
    def test_reset(self):
        tracker = LatencyTracker()
        with tracker.track('retrieval'):
            pass
        tracker.reset()
        
        assert tracker.total_latency == 0.0
        assert tracker.retrieval_latency == 0.0
