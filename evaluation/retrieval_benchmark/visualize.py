"""Visualization for retrieval benchmark results."""
import json
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from typing import Dict, List


def load_results(results_path: str) -> Dict:
    """Load results from JSON file."""
    with open(results_path, 'r') as f:
        return json.load(f)


def plot_metric_comparison(results: Dict, metric_prefix: str, k_values: List[int], 
                          output_path: str, title: str):
    """Plot comparison of a metric across strategies."""
    strategies = list(results['results'].keys())
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    x = np.arange(len(k_values))
    width = 0.8 / len(strategies)
    
    for i, strategy in enumerate(strategies):
        values = []
        for k in k_values:
            metric_name = f"{metric_prefix}@{k}"
            mean_val = results['results'][strategy]['aggregated_metrics'][metric_name]['mean']
            values.append(mean_val)
        
        offset = (i - len(strategies)/2 + 0.5) * width
        ax.bar(x + offset, values, width, label=strategy)
    
    ax.set_xlabel('k', fontsize=12)
    ax.set_ylabel(f'{metric_prefix}@k', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(k_values)
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ Plot saved: {output_path}")


def plot_latency_comparison(results: Dict, output_path: str):
    """Plot latency comparison across strategies."""
    strategies = list(results['results'].keys())
    
    means = []
    p95s = []
    p99s = []
    
    for strategy in strategies:
        lat = results['results'][strategy]['latency_stats']
        means.append(lat['mean'] * 1000)  # Convert to ms
        p95s.append(lat['p95'] * 1000)
        p99s.append(lat['p99'] * 1000)
    
    x = np.arange(len(strategies))
    width = 0.25
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    ax.bar(x - width, means, width, label='Mean', color='#2ecc71')
    ax.bar(x, p95s, width, label='p95', color='#3498db')
    ax.bar(x + width, p99s, width, label='p99', color='#e74c3c')
    
    ax.set_xlabel('Strategy', fontsize=12)
    ax.set_ylabel('Latency (ms)', fontsize=12)
    ax.set_title('Retrieval Latency Comparison', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(strategies, rotation=45, ha='right')
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ Plot saved: {output_path}")


def plot_ablation_study(results: Dict, output_path: str):
    """Plot ablation study for hybrid alpha values."""
    hybrid_results = {k: v for k, v in results['results'].items() if k.startswith('hybrid_alpha_')}
    
    if not hybrid_results:
        print("No hybrid ablation results found")
        return
    
    alphas = []
    precision_5 = []
    recall_5 = []
    ndcg_5 = []
    
    for strategy_name, result in sorted(hybrid_results.items()):
        alpha = result['alpha']
        alphas.append(alpha)
        
        agg = result['aggregated_metrics']
        precision_5.append(agg['precision@5']['mean'])
        recall_5.append(agg['recall@5']['mean'])
        ndcg_5.append(agg['ndcg@5']['mean'])
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    ax.plot(alphas, precision_5, marker='o', linewidth=2, label='Precision@5', color='#e74c3c')
    ax.plot(alphas, recall_5, marker='s', linewidth=2, label='Recall@5', color='#3498db')
    ax.plot(alphas, ndcg_5, marker='^', linewidth=2, label='nDCG@5', color='#2ecc71')
    
    ax.set_xlabel('Alpha (Vector Weight)', fontsize=12)
    ax.set_ylabel('Metric Value', fontsize=12)
    ax.set_title('Hybrid Retrieval: Impact of Alpha Parameter', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(alpha=0.3)
    ax.set_xlim(0, 1)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ Plot saved: {output_path}")


def generate_all_plots(results_path: str, output_dir: str):
    """Generate all plots from results."""
    results = load_results(results_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    k_values = results['metadata']['k_values']
    
    # Precision comparison
    plot_metric_comparison(
        results, 'precision', k_values,
        output_dir / 'precision_comparison.png',
        'Precision@k Comparison Across Strategies'
    )
    
    # Recall comparison
    plot_metric_comparison(
        results, 'recall', k_values,
        output_dir / 'recall_comparison.png',
        'Recall@k Comparison Across Strategies'
    )
    
    # nDCG comparison
    plot_metric_comparison(
        results, 'ndcg', k_values,
        output_dir / 'ndcg_comparison.png',
        'nDCG@k Comparison Across Strategies'
    )
    
    # Latency comparison
    plot_latency_comparison(
        results,
        output_dir / 'latency_comparison.png'
    )
    
    # Ablation study
    plot_ablation_study(
        results,
        output_dir / 'ablation_study.png'
    )
    
    print(f"\n✓ All plots generated in: {output_dir}")


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python visualize.py <results_json_path>")
        sys.exit(1)
    
    results_path = sys.argv[1]
    output_dir = Path(results_path).parent.parent / 'plots'
    
    generate_all_plots(results_path, output_dir)
