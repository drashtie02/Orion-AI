"""Benchmark runner for retrieval evaluation."""
import json
import time
import yaml
import random
import numpy as np
import argparse
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime

from evaluation.retrieval_benchmark.dataset_loader import EvaluationDataset
from evaluation.retrieval_benchmark.metrics import compute_all_metrics, aggregate_metrics
from retrieval.bm25 import BM25Index
from retrieval.vector_store import VectorStore
from retrieval.hybrid import HybridRetriever


class RetrievalBenchmark:
    """Benchmark runner for retrieval strategies."""
    
    def __init__(self, config_path: str):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Set random seeds for reproducibility
        self._set_seeds(self.config['random_seed'])
        
        # Load dataset
        self.dataset = EvaluationDataset(self.config['dataset_path'])
        
        # Initialize retrievers
        self.retrievers = self._initialize_retrievers()
        
        # Create output directories
        self._create_output_dirs()
    
    def _set_seeds(self, seed: int):
        """Set random seeds for reproducibility."""
        random.seed(seed)
        np.random.seed(seed)
    
    def _initialize_retrievers(self) -> Dict:
        """Initialize all retrieval strategies."""
        index_path = self.config['index_path']
        
        retrievers = {}
        
        # BM25
        bm25 = BM25Index()
        bm25.load(index_path)
        retrievers['bm25'] = bm25
        
        # Vector
        vector = VectorStore()
        vector.load(index_path)
        retrievers['vector'] = vector
        
        # Hybrid
        hybrid = HybridRetriever()
        hybrid.load(index_path)
        retrievers['hybrid'] = hybrid
        
        return retrievers
    
    def _create_output_dirs(self):
        """Create output directories."""
        Path(self.config['results_dir']).mkdir(parents=True, exist_ok=True)
        Path(self.config['plots_dir']).mkdir(parents=True, exist_ok=True)
        Path(self.config['tables_dir']).mkdir(parents=True, exist_ok=True)
    
    def _retrieve_bm25(self, query: str, top_k: int) -> Tuple[List[str], float]:
        """Retrieve using BM25."""
        start = time.time()
        results = self.retrievers['bm25'].search(query, top_k)
        latency = time.time() - start
        
        retrieved_ids = [chunk['chunk_id'] for chunk, _ in results]
        return retrieved_ids, latency
    
    def _retrieve_vector(self, query: str, top_k: int) -> Tuple[List[str], float]:
        """Retrieve using vector search."""
        start = time.time()
        results = self.retrievers['vector'].search(query, top_k)
        latency = time.time() - start
        
        retrieved_ids = [chunk['chunk_id'] for chunk, _ in results]
        return retrieved_ids, latency
    
    def _retrieve_hybrid(self, query: str, top_k: int, alpha: float = 0.5) -> Tuple[List[str], float, Dict]:
        """Retrieve using hybrid search."""
        self.retrievers['hybrid'].set_alpha(alpha)
        
        start = time.time()
        results = self.retrievers['hybrid'].search(query, top_k)
        latency = time.time() - start
        
        retrieved_ids = [r['chunk']['chunk_id'] for r in results]
        
        # Latency breakdown
        breakdown = {
            'total': latency,
            'bm25': latency * 0.4,  # Approximate
            'vector': latency * 0.4,
            'combination': latency * 0.2
        }
        
        return retrieved_ids, latency, breakdown
    
    def run_strategy(self, strategy: str, alpha: float = None) -> Dict:
        """Run evaluation for a single strategy."""
        print(f"\n{'='*60}")
        print(f"Running: {strategy}" + (f" (alpha={alpha})" if alpha else ""))
        print(f"{'='*60}")
        
        top_k = self.config['top_k_retrieve']
        k_values = self.config['k_values']
        
        query_results = []
        latencies = []
        
        for query_data in self.dataset:
            query_id = query_data['query_id']
            query = query_data['query']
            relevant = self.dataset.get_relevant_chunks(query_id)
            
            # Retrieve
            if strategy == 'bm25':
                retrieved, latency = self._retrieve_bm25(query, top_k)
            elif strategy == 'vector':
                retrieved, latency = self._retrieve_vector(query, top_k)
            elif strategy == 'hybrid':
                alpha_val = alpha if alpha is not None else 0.5
                retrieved, latency, _ = self._retrieve_hybrid(query, top_k, alpha_val)
            else:
                raise ValueError(f"Unknown strategy: {strategy}")
            
            # Compute metrics
            metrics = compute_all_metrics(retrieved, relevant, k_values)
            
            query_results.append({
                'query_id': query_id,
                'query': query,
                'retrieved': retrieved,
                'relevant': list(relevant),
                'metrics': metrics,
                'latency': latency
            })
            
            latencies.append(latency)
            
            print(f"  {query_id}: P@5={metrics['precision@5']:.3f}, "
                  f"R@5={metrics['recall@5']:.3f}, "
                  f"nDCG@5={metrics['ndcg@5']:.3f}, "
                  f"latency={latency*1000:.1f}ms")
        
        # Aggregate metrics
        all_metrics = [qr['metrics'] for qr in query_results]
        aggregated = aggregate_metrics(all_metrics)
        
        # Latency statistics
        latency_stats = {
            'mean': float(np.mean(latencies)),
            'std': float(np.std(latencies)),
            'p50': float(np.percentile(latencies, 50)),
            'p95': float(np.percentile(latencies, 95)),
            'p99': float(np.percentile(latencies, 99)),
            'min': float(np.min(latencies)),
            'max': float(np.max(latencies))
        }
        
        return {
            'strategy': strategy,
            'alpha': alpha,
            'query_results': query_results,
            'aggregated_metrics': aggregated,
            'latency_stats': latency_stats,
            'num_queries': len(query_results)
        }
    
    def run_all_strategies(self) -> Dict:
        """Run all configured strategies."""
        results = {}
        
        for strategy in self.config['strategies']:
            if strategy == 'hybrid':
                # Run hybrid with different alphas
                for alpha in self.config['hybrid_alphas']:
                    key = f"hybrid_alpha_{alpha}"
                    results[key] = self.run_strategy('hybrid', alpha=alpha)
            else:
                results[strategy] = self.run_strategy(strategy)
        
        return results
    
    def save_results(self, results: Dict, filename: str = None):
        """Save results to JSON."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"results_{timestamp}.json"
        
        output_path = Path(self.config['results_dir']) / filename
        
        # Add metadata
        output = {
            'metadata': {
                'experiment_name': self.config['experiment_name'],
                'description': self.config['description'],
                'timestamp': datetime.now().isoformat(),
                'random_seed': self.config['random_seed'],
                'num_queries': len(self.dataset),
                'k_values': self.config['k_values']
            },
            'results': results
        }
        
        with open(output_path, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"\n✓ Results saved to: {output_path}")
        return output_path
    
    def generate_comparison_table(self, results: Dict) -> str:
        """Generate comparison table in markdown format."""
        k_values = self.config['k_values']
        
        # Header
        table = "# Retrieval Strategy Comparison\n\n"
        table += "## Effectiveness Metrics\n\n"
        table += "| Strategy | " + " | ".join([f"P@{k}" for k in k_values]) + " | "
        table += " | ".join([f"R@{k}" for k in k_values]) + " | "
        table += " | ".join([f"nDCG@{k}" for k in k_values]) + " | MRR |\n"
        table += "|" + "---|" * (1 + len(k_values) * 3 + 1) + "\n"
        
        # Rows
        for strategy_name, result in results.items():
            agg = result['aggregated_metrics']
            row = f"| {strategy_name} |"
            
            for k in k_values:
                row += f" {agg[f'precision@{k}']['mean']:.4f} |"
            for k in k_values:
                row += f" {agg[f'recall@{k}']['mean']:.4f} |"
            for k in k_values:
                row += f" {agg[f'ndcg@{k}']['mean']:.4f} |"
            row += f" {agg['mrr']['mean']:.4f} |\n"
            
            table += row
        
        # Latency table
        table += "\n## Latency (seconds)\n\n"
        table += "| Strategy | Mean | Std | p50 | p95 | p99 |\n"
        table += "|---|---|---|---|---|---|\n"
        
        for strategy_name, result in results.items():
            lat = result['latency_stats']
            table += f"| {strategy_name} | {lat['mean']:.4f} | {lat['std']:.4f} | "
            table += f"{lat['p50']:.4f} | {lat['p95']:.4f} | {lat['p99']:.4f} |\n"
        
        return table
    
    def save_table(self, results: Dict, filename: str = "comparison_table.md"):
        """Save comparison table."""
        table = self.generate_comparison_table(results)
        output_path = Path(self.config['tables_dir']) / filename
        
        with open(output_path, 'w') as f:
            f.write(table)
        
        print(f"✓ Table saved to: {output_path}")
        return output_path


def main():
    parser = argparse.ArgumentParser(description='Run retrieval benchmark')
    parser.add_argument('--config', type=str, 
                       default='evaluation/retrieval_benchmark/config.yaml',
                       help='Path to config file')
    parser.add_argument('--strategy', type=str, choices=['bm25', 'vector', 'hybrid', 'all'],
                       default='all', help='Strategy to run')
    parser.add_argument('--alpha', type=float, default=None,
                       help='Alpha value for hybrid (only used with --strategy hybrid)')
    
    args = parser.parse_args()
    
    # Initialize benchmark
    benchmark = RetrievalBenchmark(args.config)
    
    # Run experiments
    if args.strategy == 'all':
        results = benchmark.run_all_strategies()
    else:
        results = {args.strategy: benchmark.run_strategy(args.strategy, alpha=args.alpha)}
    
    # Save results
    benchmark.save_results(results)
    benchmark.save_table(results)
    
    print("\n" + "="*60)
    print("Benchmark completed successfully!")
    print("="*60)


if __name__ == '__main__':
    main()
