"""Information Retrieval metrics for evaluation."""
import numpy as np
from typing import List, Set, Dict


def precision_at_k(retrieved: List[str], relevant: Set[str], k: int) -> float:
    """
    Precision@k: Fraction of retrieved documents in top-k that are relevant.
    
    P@k = |relevant ∩ retrieved[:k]| / k
    """
    if k == 0:
        return 0.0
    
    retrieved_at_k = retrieved[:k]
    relevant_retrieved = len(set(retrieved_at_k) & relevant)
    return relevant_retrieved / k


def recall_at_k(retrieved: List[str], relevant: Set[str], k: int) -> float:
    """
    Recall@k: Fraction of relevant documents that are retrieved in top-k.
    
    R@k = |relevant ∩ retrieved[:k]| / |relevant|
    """
    if len(relevant) == 0:
        return 0.0
    
    retrieved_at_k = retrieved[:k]
    relevant_retrieved = len(set(retrieved_at_k) & relevant)
    return relevant_retrieved / len(relevant)


def f1_at_k(retrieved: List[str], relevant: Set[str], k: int) -> float:
    """
    F1@k: Harmonic mean of precision and recall at k.
    
    F1@k = 2 * (P@k * R@k) / (P@k + R@k)
    """
    p = precision_at_k(retrieved, relevant, k)
    r = recall_at_k(retrieved, relevant, k)
    
    if p + r == 0:
        return 0.0
    
    return 2 * (p * r) / (p + r)


def mean_reciprocal_rank(retrieved: List[str], relevant: Set[str]) -> float:
    """
    Mean Reciprocal Rank: Reciprocal of rank of first relevant document.
    
    MRR = 1 / rank(first_relevant_doc)
    
    Returns 0 if no relevant documents are retrieved.
    """
    for i, doc_id in enumerate(retrieved, start=1):
        if doc_id in relevant:
            return 1.0 / i
    return 0.0


def dcg_at_k(retrieved: List[str], relevant: Set[str], k: int) -> float:
    """
    Discounted Cumulative Gain at k.
    
    DCG@k = Σ(rel_i / log2(i + 1)) for i in [1, k]
    
    Binary relevance: rel_i = 1 if relevant, 0 otherwise.
    """
    dcg = 0.0
    for i, doc_id in enumerate(retrieved[:k], start=1):
        if doc_id in relevant:
            dcg += 1.0 / np.log2(i + 1)
    return dcg


def ndcg_at_k(retrieved: List[str], relevant: Set[str], k: int) -> float:
    """
    Normalized Discounted Cumulative Gain at k.
    
    nDCG@k = DCG@k / IDCG@k
    
    IDCG@k is the ideal DCG (all relevant docs at top positions).
    """
    dcg = dcg_at_k(retrieved, relevant, k)
    
    # Ideal DCG: all relevant docs at top positions
    ideal_retrieved = list(relevant) + ['dummy'] * k
    idcg = dcg_at_k(ideal_retrieved, relevant, k)
    
    if idcg == 0:
        return 0.0
    
    return dcg / idcg


def compute_all_metrics(retrieved: List[str], relevant: Set[str], k_values: List[int]) -> Dict[str, float]:
    """
    Compute all metrics for given k values.
    
    Args:
        retrieved: List of retrieved document IDs in ranked order
        relevant: Set of relevant document IDs
        k_values: List of k values to compute metrics for
    
    Returns:
        Dictionary of metric_name -> value
    """
    metrics = {}
    
    for k in k_values:
        metrics[f'precision@{k}'] = precision_at_k(retrieved, relevant, k)
        metrics[f'recall@{k}'] = recall_at_k(retrieved, relevant, k)
        metrics[f'f1@{k}'] = f1_at_k(retrieved, relevant, k)
        metrics[f'ndcg@{k}'] = ndcg_at_k(retrieved, relevant, k)
    
    metrics['mrr'] = mean_reciprocal_rank(retrieved, relevant)
    
    return metrics


def aggregate_metrics(all_query_metrics: List[Dict[str, float]]) -> Dict[str, Dict[str, float]]:
    """
    Aggregate metrics across all queries.
    
    Returns:
        Dictionary with mean, std, min, max for each metric
    """
    if not all_query_metrics:
        return {}
    
    metric_names = all_query_metrics[0].keys()
    aggregated = {}
    
    for metric_name in metric_names:
        values = [m[metric_name] for m in all_query_metrics]
        aggregated[metric_name] = {
            'mean': float(np.mean(values)),
            'std': float(np.std(values)),
            'min': float(np.min(values)),
            'max': float(np.max(values))
        }
    
    return aggregated
