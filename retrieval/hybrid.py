from typing import List, Dict
from retrieval.vector_store import VectorStore
from retrieval.bm25 import BM25Index
from core.config import config

class HybridRetriever:
    def __init__(self, alpha=None):
        self.vector_store = VectorStore()
        self.bm25_index = BM25Index()
        self.alpha = alpha if alpha is not None else config.retrieval_alpha
        self.embedding_model = self.vector_store.model
    
    def load(self, index_path: str):
        self.vector_store.load(index_path)
        self.bm25_index.load(index_path)
    
    def search(self, query: str, top_k: int) -> List[Dict]:
        vector_results = self.vector_store.search(query, top_k * 2)
        bm25_results = self.bm25_index.search(query, top_k * 2)
        
        vector_scores = {i: score for i, (chunk, score) in enumerate(vector_results)}
        bm25_scores = {i: score for i, (chunk, score) in enumerate(bm25_results)}
        
        vector_scores_norm = self._normalize_scores(list(vector_scores.values()))
        bm25_scores_norm = self._normalize_scores(list(bm25_scores.values()))
        
        combined = {}
        all_chunks = {}
        
        for i, (chunk, _) in enumerate(vector_results):
            chunk_id = chunk['chunk_id']
            all_chunks[chunk_id] = chunk
            combined[chunk_id] = {
                'vector_score': vector_scores_norm[i],
                'bm25_score': 0.0
            }
        
        for i, (chunk, _) in enumerate(bm25_results):
            chunk_id = chunk['chunk_id']
            all_chunks[chunk_id] = chunk
            if chunk_id not in combined:
                combined[chunk_id] = {'vector_score': 0.0, 'bm25_score': bm25_scores_norm[i]}
            else:
                combined[chunk_id]['bm25_score'] = bm25_scores_norm[i]
        
        results = []
        for chunk_id, scores in combined.items():
            hybrid_score = self.alpha * scores['vector_score'] + (1 - self.alpha) * scores['bm25_score']
            results.append({
                'chunk': all_chunks[chunk_id],
                'vector_score': scores['vector_score'],
                'bm25_score': scores['bm25_score'],
                'hybrid_score': hybrid_score
            })
        
        results.sort(key=lambda x: x['hybrid_score'], reverse=True)
        return results[:top_k]
    
    def set_alpha(self, alpha: float):
        self.alpha = alpha
    
    def _normalize_scores(self, scores: List[float]) -> List[float]:
        if not scores or max(scores) == min(scores):
            return [0.0] * len(scores)
        min_score = min(scores)
        max_score = max(scores)
        return [(s - min_score) / (max_score - min_score) for s in scores]
