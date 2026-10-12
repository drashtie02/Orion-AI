"""Unit tests for retrieval metrics."""
import pytest
from evaluation.retrieval_benchmark.metrics import (
    precision_at_k, recall_at_k, f1_at_k, 
    mean_reciprocal_rank, ndcg_at_k, compute_all_metrics
)


class TestPrecisionAtK:
    def test_perfect_precision(self):
        retrieved = ['doc1', 'doc2', 'doc3']
        relevant = {'doc1', 'doc2', 'doc3'}
        assert precision_at_k(retrieved, relevant, 3) == 1.0
    
    def test_zero_precision(self):
        retrieved = ['doc1', 'doc2', 'doc3']
        relevant = {'doc4', 'doc5'}
        assert precision_at_k(retrieved, relevant, 3) == 0.0
    
    def test_partial_precision(self):
        retrieved = ['doc1', 'doc2', 'doc3', 'doc4']
        relevant = {'doc1', 'doc3'}
        assert precision_at_k(retrieved, relevant, 4) == 0.5
    
    def test_k_larger_than_retrieved(self):
        retrieved = ['doc1', 'doc2']
        relevant = {'doc1', 'doc2'}
        # Should only consider first k items
        assert precision_at_k(retrieved, relevant, 5) == 0.4


class TestRecallAtK:
    def test_perfect_recall(self):
        retrieved = ['doc1', 'doc2', 'doc3']
        relevant = {'doc1', 'doc2'}
        assert recall_at_k(retrieved, relevant, 3) == 1.0
    
    def test_zero_recall(self):
        retrieved = ['doc1', 'doc2']
        relevant = {'doc3', 'doc4'}
        assert recall_at_k(retrieved, relevant, 2) == 0.0
    
    def test_partial_recall(self):
        retrieved = ['doc1', 'doc2', 'doc3']
        relevant = {'doc1', 'doc4', 'doc5', 'doc6'}
        assert recall_at_k(retrieved, relevant, 3) == 0.25
    
    def test_empty_relevant(self):
        retrieved = ['doc1', 'doc2']
        relevant = set()
        assert recall_at_k(retrieved, relevant, 2) == 0.0


class TestF1AtK:
    def test_perfect_f1(self):
        retrieved = ['doc1', 'doc2']
        relevant = {'doc1', 'doc2'}
        assert f1_at_k(retrieved, relevant, 2) == 1.0
    
    def test_zero_f1(self):
        retrieved = ['doc1', 'doc2']
        relevant = {'doc3', 'doc4'}
        assert f1_at_k(retrieved, relevant, 2) == 0.0
    
    def test_f1_calculation(self):
        retrieved = ['doc1', 'doc2', 'doc3', 'doc4']
        relevant = {'doc1', 'doc3'}
        # P@4 = 2/4 = 0.5, R@4 = 2/2 = 1.0
        # F1 = 2 * (0.5 * 1.0) / (0.5 + 1.0) = 2/3
        assert abs(f1_at_k(retrieved, relevant, 4) - 2/3) < 1e-6


class TestMRR:
    def test_first_position(self):
        retrieved = ['doc1', 'doc2', 'doc3']
        relevant = {'doc1'}
        assert mean_reciprocal_rank(retrieved, relevant) == 1.0
    
    def test_second_position(self):
        retrieved = ['doc1', 'doc2', 'doc3']
        relevant = {'doc2'}
        assert mean_reciprocal_rank(retrieved, relevant) == 0.5
    
    def test_third_position(self):
        retrieved = ['doc1', 'doc2', 'doc3']
        relevant = {'doc3'}
        assert abs(mean_reciprocal_rank(retrieved, relevant) - 1/3) < 1e-6
    
    def test_no_relevant(self):
        retrieved = ['doc1', 'doc2', 'doc3']
        relevant = {'doc4'}
        assert mean_reciprocal_rank(retrieved, relevant) == 0.0


class TestNDCGAtK:
    def test_perfect_ndcg(self):
        retrieved = ['doc1', 'doc2', 'doc3']
        relevant = {'doc1', 'doc2', 'doc3'}
        assert ndcg_at_k(retrieved, relevant, 3) == 1.0
    
    def test_zero_ndcg(self):
        retrieved = ['doc1', 'doc2', 'doc3']
        relevant = {'doc4', 'doc5'}
        assert ndcg_at_k(retrieved, relevant, 3) == 0.0
    
    def test_partial_ndcg(self):
        # First relevant doc at position 2
        retrieved = ['doc1', 'doc2', 'doc3']
        relevant = {'doc2'}
        # DCG = 1/log2(3) ≈ 0.631
        # IDCG = 1/log2(2) = 1.0
        # nDCG ≈ 0.631
        ndcg = ndcg_at_k(retrieved, relevant, 3)
        assert 0.6 < ndcg < 0.7


class TestComputeAllMetrics:
    def test_all_metrics_computed(self):
        retrieved = ['doc1', 'doc2', 'doc3', 'doc4', 'doc5']
        relevant = {'doc1', 'doc3', 'doc5'}
        k_values = [1, 3, 5]
        
        metrics = compute_all_metrics(retrieved, relevant, k_values)
        
        # Check all expected metrics are present
        for k in k_values:
            assert f'precision@{k}' in metrics
            assert f'recall@{k}' in metrics
            assert f'f1@{k}' in metrics
            assert f'ndcg@{k}' in metrics
        
        assert 'mrr' in metrics
    
    def test_metrics_values_valid(self):
        retrieved = ['doc1', 'doc2', 'doc3']
        relevant = {'doc1', 'doc2'}
        k_values = [3]
        
        metrics = compute_all_metrics(retrieved, relevant, k_values)
        
        # All metrics should be between 0 and 1
        for value in metrics.values():
            assert 0.0 <= value <= 1.0
