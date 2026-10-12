import pytest
from unittest.mock import Mock
import numpy as np
from evaluation.evaluator import Evaluator
from evaluation.faithfulness import FaithfulnessEvaluator
from evaluation.relevance import RelevanceEvaluator
from evaluation.hallucination import HallucinationDetector

@pytest.fixture
def mock_embedding_model():
    model = Mock()
    model.encode = Mock(return_value=np.array([[0.1, 0.2, 0.3]]))
    return model

class TestEvaluator:
    def test_initialization(self, mock_embedding_model):
        evaluator = Evaluator(mock_embedding_model)
        
        assert evaluator.faithfulness_evaluator is not None
        assert evaluator.relevance_evaluator is not None
        assert evaluator.hallucination_detector is not None
        assert evaluator.weights is not None
    
    def test_initialization_with_custom_weights(self, mock_embedding_model):
        custom_weights = {
            'faithfulness': 0.4,
            'relevance': 0.3,
            'hallucination': 0.2,
            'source_coverage': 0.1
        }
        evaluator = Evaluator(mock_embedding_model, weights=custom_weights)
        
        assert evaluator.weights == custom_weights
    
    def test_compute_source_coverage(self, mock_embedding_model):
        evaluator = Evaluator(mock_embedding_model)
        
        answer = "machine learning is great"
        context = ["machine learning", "is awesome"]
        
        coverage = evaluator._compute_source_coverage(answer, context)
        
        assert coverage > 0.0
        assert coverage <= 1.0
    
    def test_compute_source_coverage_empty_context(self, mock_embedding_model):
        evaluator = Evaluator(mock_embedding_model)
        
        coverage = evaluator._compute_source_coverage("test", [])
        
        assert coverage == 0.0
    
    def test_compute_source_coverage_empty_answer(self, mock_embedding_model):
        evaluator = Evaluator(mock_embedding_model)
        
        coverage = evaluator._compute_source_coverage("", ["context"])
        
        assert coverage == 1.0
    
    def test_evaluate_success(self, mock_embedding_model):
        evaluator = Evaluator(mock_embedding_model)
        
        result = evaluator.evaluate(
            "What is ML?",
            "Machine learning is AI",
            ["Machine learning", "Artificial intelligence"]
        )
        
        assert result is not None
        assert 'faithfulness' in result
        assert 'relevance' in result
        assert 'hallucination' in result
        assert 'confidence_score' in result
    
    def test_evaluate_with_exception(self, mock_embedding_model):
        evaluator = Evaluator(mock_embedding_model)
        evaluator.faithfulness_evaluator.evaluate = Mock(side_effect=Exception("Error"))
        
        result = evaluator.evaluate("query", "answer", ["context"])
        
        assert result is None

class TestFaithfulnessEvaluator:
    def test_initialization(self, mock_embedding_model):
        evaluator = FaithfulnessEvaluator(mock_embedding_model)
        
        assert evaluator.embedding_model is not None
        assert evaluator.threshold == 0.5
    
    def test_split_sentences(self, mock_embedding_model):
        evaluator = FaithfulnessEvaluator(mock_embedding_model)
        
        text = "First sentence. Second sentence! Third sentence?"
        sentences = evaluator._split_sentences(text)
        
        assert len(sentences) == 3
    
    def test_split_sentences_empty(self, mock_embedding_model):
        evaluator = FaithfulnessEvaluator(mock_embedding_model)
        
        sentences = evaluator._split_sentences("")
        
        assert len(sentences) == 0
    
    def test_compute_similarity(self, mock_embedding_model):
        evaluator = FaithfulnessEvaluator(mock_embedding_model)
        
        sim = evaluator._compute_similarity("text1", "text2")
        
        assert isinstance(sim, float)
        assert sim >= -1.0 and sim <= 1.0
    
    def test_compute_similarity_zero_norm(self, mock_embedding_model):
        mock_embedding_model.encode = Mock(return_value=np.array([[0.0, 0.0, 0.0]]))
        evaluator = FaithfulnessEvaluator(mock_embedding_model)
        
        sim = evaluator._compute_similarity("text1", "text2")
        
        assert sim == 0.0
    
    def test_evaluate_empty_answer(self, mock_embedding_model):
        evaluator = FaithfulnessEvaluator(mock_embedding_model)
        
        result = evaluator.evaluate("", ["context"])
        
        assert result['faithfulness_score'] == 1.0
        assert len(result['unsupported_sentences']) == 0
    
    def test_evaluate_with_context(self, mock_embedding_model):
        evaluator = FaithfulnessEvaluator(mock_embedding_model)
        
        result = evaluator.evaluate(
            "Machine learning is great.",
            ["Machine learning", "Deep learning"]
        )
        
        assert 'faithfulness_score' in result
        assert 'unsupported_sentences' in result

class TestRelevanceEvaluator:
    def test_initialization(self, mock_embedding_model):
        evaluator = RelevanceEvaluator(mock_embedding_model)
        
        assert evaluator.embedding_model is not None
    
    def test_evaluate(self, mock_embedding_model):
        evaluator = RelevanceEvaluator(mock_embedding_model)
        
        result = evaluator.evaluate("query", ["context1", "context2"])
        
        assert 'context_relevance_score' in result

class TestHallucinationDetector:
    def test_initialization(self):
        detector = HallucinationDetector()
        
        assert detector is not None
    
    def test_evaluate(self):
        detector = HallucinationDetector()
        
        result = detector.evaluate("answer", ["context"])
        
        assert 'hallucination_risk' in result
        assert result['hallucination_risk'] >= 0.0
        assert result['hallucination_risk'] <= 1.0
    
    def test_evaluate_empty_context(self):
        detector = HallucinationDetector()
        
        result = detector.evaluate("answer", [])
        
        assert result['hallucination_risk'] >= 0.0
