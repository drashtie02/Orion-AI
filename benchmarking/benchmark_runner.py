import yaml
import json
import numpy as np
from typing import Dict, List
from pathlib import Path
import sys
import logging

sys.path.append(str(Path(__file__).parent.parent))

from retrieval.hybrid import HybridRetriever
from llm.router import LLMRouter
from evaluation.evaluator import Evaluator
from core.orchestrator import Orchestrator
from core.config import config

logger = logging.getLogger(__name__)

class BenchmarkRunner:
    def __init__(self, dataset_path: str, experiments_path: str, index_path: str):
        with open(dataset_path) as f:
            self.dataset = json.load(f)
        
        with open(experiments_path) as f:
            self.experiments_config = yaml.safe_load(f)
        
        self.index_path = index_path
        self.llm_router = LLMRouter()
    
    def _compute_ground_truth_similarity(self, answer: str, ground_truth: str, embedding_model) -> float:
        emb1 = embedding_model.encode([answer])[0]
        emb2 = embedding_model.encode([ground_truth])[0]
        norm1 = np.linalg.norm(emb1)
        norm2 = np.linalg.norm(emb2)
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return float(np.dot(emb1, emb2) / (norm1 * norm2))
    
    def run_experiment(self, experiment: Dict) -> Dict:
        name = experiment['name']
        alpha = experiment['alpha']
        retry_enabled = experiment['retry_enabled']
        routing_mode = experiment.get('routing_mode', None)
        
        logger.info(f"Experiment: {name} alpha={alpha} retry={retry_enabled} routing={routing_mode}")
        
        retriever = HybridRetriever(alpha=alpha)
        retriever.load(self.index_path)
        
        evaluator = Evaluator(retriever.embedding_model, config.evaluation_weights)
        
        model_router = None
        if routing_mode and config.models:
            from core.model_router import ModelRouter
            if routing_mode == 'dynamic':
                model_router = ModelRouter(
                    self.llm_router,
                    config.routing_config['cheap_model'],
                    config.routing_config['strong_model'],
                    config.routing_config['token_threshold'],
                    config.routing_config['confidence_threshold']
                )
            elif routing_mode == 'cheap_only':
                model_router = ModelRouter(
                    self.llm_router,
                    config.routing_config['cheap_model'],
                    config.routing_config['cheap_model'],
                    999999,
                    0.0
                )
            elif routing_mode == 'strong_only':
                model_router = ModelRouter(
                    self.llm_router,
                    config.routing_config['strong_model'],
                    config.routing_config['strong_model'],
                    0,
                    1.0
                )
        
        orchestrator = Orchestrator(
            retriever,
            self.llm_router,
            evaluator,
            config.critic_threshold,
            retry_enabled,
            model_router,
            None
        )
        
        results = []
        for item in self.dataset:
            query = item['query']
            ground_truth = item['ground_truth']
            
            try:
                result = orchestrator.execute(query, config.top_k_default)
                
                evaluation = result.get('evaluation', {})
                if evaluation:
                    faithfulness = evaluation.get('faithfulness', {}).get('faithfulness_score', 0.0)
                    relevance = evaluation.get('relevance', {}).get('context_relevance_score', 0.0)
                    hallucination = evaluation.get('hallucination', {}).get('hallucination_risk', 0.0)
                    confidence = evaluation.get('confidence_score', 0.0)
                else:
                    faithfulness = relevance = confidence = 0.0
                    hallucination = 1.0
                
                total_latency = sum(step['latency'] for step in result.get('trace', []))
                total_tokens = sum(
                    step['tokens'].get('input_tokens', 0) + step['tokens'].get('output_tokens', 0)
                    for step in result.get('trace', [])
                )
                
                routing_info = result.get('routing', {})
                estimated_cost = routing_info.get('estimated_cost', 0.0)
                
                answer = result.get('answer', '')
                gt_similarity = self._compute_ground_truth_similarity(
                    answer, ground_truth, retriever.embedding_model
                )
                
                results.append({
                    'faithfulness': faithfulness,
                    'relevance': relevance,
                    'hallucination': hallucination,
                    'confidence': confidence,
                    'latency': total_latency,
                    'tokens': total_tokens,
                    'ground_truth_similarity': gt_similarity,
                    'cost': estimated_cost
                })
            
            except Exception as e:
                logger.error(f"Query failed: {str(e)}")
                results.append({
                    'faithfulness': 0.0,
                    'relevance': 0.0,
                    'hallucination': 1.0,
                    'confidence': 0.0,
                    'latency': 0.0,
                    'tokens': 0,
                    'ground_truth_similarity': 0.0,
                    'cost': 0.0
                })
        
        avg_cost = float(np.mean([r['cost'] for r in results]))
        cost_efficiency = (float(np.mean([r['confidence'] for r in results])) / avg_cost) if avg_cost > 0 else 0.0
        
        return {
            'experiment_name': name,
            'avg_faithfulness': float(np.mean([r['faithfulness'] for r in results])),
            'avg_relevance': float(np.mean([r['relevance'] for r in results])),
            'avg_hallucination': float(np.mean([r['hallucination'] for r in results])),
            'avg_confidence': float(np.mean([r['confidence'] for r in results])),
            'avg_latency': float(np.mean([r['latency'] for r in results])),
            'avg_tokens': float(np.mean([r['tokens'] for r in results])),
            'avg_ground_truth_similarity': float(np.mean([r['ground_truth_similarity'] for r in results])),
            'avg_cost': avg_cost,
            'cost_efficiency': cost_efficiency
        }
    
    def run_all(self) -> List[Dict]:
        results = []
        for experiment in self.experiments_config['experiments']:
            result = self.run_experiment(experiment)
            results.append(result)
        return results
