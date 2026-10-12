import sys
import json
from pathlib import Path
from datetime import datetime

sys.path.append(str(Path(__file__).parent.parent))

from benchmarking.benchmark_runner import BenchmarkRunner
from core.config import config

def print_summary_table(results):
    print("\n" + "="*120)
    print("BENCHMARK RESULTS")
    print("="*120)
    print(f"{'Experiment':<25} {'Confidence':<12} {'Faithfulness':<14} {'Cost':<10} {'Efficiency':<12} {'Latency':<10}")
    print("-"*120)
    
    for result in results:
        print(f"{result['experiment_name']:<25} "
              f"{result['avg_confidence']:<12.4f} "
              f"{result['avg_faithfulness']:<14.4f} "
              f"{result['avg_cost']:<10.6f} "
              f"{result['cost_efficiency']:<12.4f} "
              f"{result['avg_latency']:<10.2f}")
    
    print("="*120 + "\n")

def main():
    dataset_path = "benchmarking/benchmark_dataset.json"
    experiments_path = "benchmarking/experiments.yaml"
    index_path = config.index_path
    
    if not Path(f"{index_path}/faiss.index").exists():
        print(f"Error: Index not found at {index_path}. Run ingestion first.")
        return
    
    runner = BenchmarkRunner(dataset_path, experiments_path, index_path)
    results = runner.run_all()
    
    results_sorted = sorted(results, key=lambda x: (-x['avg_confidence'], x['avg_latency']))
    
    best_by_confidence = results_sorted[0]['experiment_name']
    fastest = min(results, key=lambda x: x['avg_latency'])['experiment_name']
    best_cost_efficiency = max(results, key=lambda x: x.get('cost_efficiency', 0.0))['experiment_name']
    
    output = {
        'timestamp': datetime.now().isoformat(),
        'results': results_sorted,
        'best_by_confidence': best_by_confidence,
        'fastest_configuration': fastest,
        'best_cost_efficiency': best_cost_efficiency
    }
    
    output_path = Path("artifacts/benchmark_results.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)
    
    print_summary_table(results_sorted)
    print(f"Best by confidence: {best_by_confidence}")
    print(f"Fastest configuration: {fastest}")
    print(f"Best cost efficiency: {best_cost_efficiency}")
    print(f"\nResults saved to: {output_path}")

if __name__ == "__main__":
    main()
