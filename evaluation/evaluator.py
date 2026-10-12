from typing import List, Dict
import logging
from .faithfulness import FaithfulnessEvaluator
from .relevance import RelevanceEvaluator
from .hallucination import HallucinationDetector

logger = logging.getLogger(__name__)

class Evaluator:
    def __init__(self, embedding_model, weights: Dict[str, float] = None):
        self.faithfulness_evaluator = FaithfulnessEvaluator(embedding_model)
        self.relevance_evaluator = RelevanceEvaluator(embedding_model)
        self.hallucination_detector = HallucinationDetector()
        
        self.weights = weights or {
            'faithfulness': 0.3,
            'relevance': 0.2,
            'hallucination': 0.3,
            'source_coverage': 0.2
        }
    
    def _compute_source_coverage(self, answer: str, context_chunks: List[str]) -> float:
        if not context_chunks:
            return 0.0
        
        answer_words = set(answer.lower().split())
        context_words = set(" ".join(context_chunks).lower().split())
        
        if not answer_words:
            return 1.0
        
        overlap = answer_words.intersection(context_words)
        coverage = len(overlap) / len(answer_words)
        
        return coverage
    
    def evaluate(self, query: str, answer: str, context_chunks: List[str]) -> Dict:
        try:
            faithfulness_result = self.faithfulness_evaluator.evaluate(answer, context_chunks)
            relevance_result = self.relevance_evaluator.evaluate(query, context_chunks)
            hallucination_result = self.hallucination_detector.evaluate(answer, context_chunks)
            source_coverage = self._compute_source_coverage(answer, context_chunks)
            
            confidence_score = (
                self.weights['faithfulness'] * faithfulness_result['faithfulness_score'] +
                self.weights['relevance'] * relevance_result['context_relevance_score'] +
                self.weights['hallucination'] * (1 - hallucination_result['hallucination_risk']) +
                self.weights['source_coverage'] * source_coverage
            )
            
            logger.info(f"Evaluation: faithfulness={faithfulness_result['faithfulness_score']:.3f} hallucination={hallucination_result['hallucination_risk']:.3f} confidence={confidence_score:.3f}")
            
            return {
                'faithfulness': faithfulness_result,
                'relevance': relevance_result,
                'hallucination': hallucination_result,
                'source_coverage': {'source_coverage_score': source_coverage},
                'confidence_score': confidence_score
            }
        except Exception as e:
            logger.error(f"Evaluation failed: {str(e)}")
            return None
