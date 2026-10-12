import numpy as np
import torch
from typing import List, Dict

class RelevanceEvaluator:
    def __init__(self, embedding_model):
        self.embedding_model = embedding_model
    
    def _compute_similarity(self, text1: str, text2: str) -> float:
        emb1 = self.embedding_model.encode([text1], convert_to_numpy=True)[0]
        emb2 = self.embedding_model.encode([text2], convert_to_numpy=True)[0]
        norm1 = np.linalg.norm(emb1)
        norm2 = np.linalg.norm(emb2)
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return float(np.dot(emb1, emb2) / (norm1 * norm2))
    
    def evaluate(self, query: str, context_chunks: List[str]) -> Dict:
        if not context_chunks:
            return {"context_relevance_score": 0.0}
        
        similarities = []
        for chunk in context_chunks:
            sim = self._compute_similarity(query, chunk)
            similarities.append(sim)
        
        relevance_score = float(np.mean(similarities))
        
        return {
            "context_relevance_score": relevance_score
        }
