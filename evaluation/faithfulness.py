import numpy as np
import torch
from typing import List, Dict
import re

class FaithfulnessEvaluator:
    def __init__(self, embedding_model):
        self.embedding_model = embedding_model
        self.threshold = 0.5
    
    def _split_sentences(self, text: str) -> List[str]:
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _compute_similarity(self, text1: str, text2: str) -> float:
        emb1 = self.embedding_model.encode([text1], convert_to_numpy=True)[0]
        emb2 = self.embedding_model.encode([text2], convert_to_numpy=True)[0]
        norm1 = np.linalg.norm(emb1)
        norm2 = np.linalg.norm(emb2)
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return float(np.dot(emb1, emb2) / (norm1 * norm2))
    
    def evaluate(self, answer: str, context_chunks: List[str]) -> Dict:
        sentences = self._split_sentences(answer)
        if not sentences:
            return {"faithfulness_score": 1.0, "unsupported_sentences": []}
        
        context_text = " ".join(context_chunks)
        unsupported = []
        scores = []
        
        for sentence in sentences:
            max_sim = 0.0
            for chunk in context_chunks:
                sim = self._compute_similarity(sentence, chunk)
                max_sim = max(max_sim, sim)
            
            scores.append(max_sim)
            if max_sim < self.threshold:
                unsupported.append(sentence)
        
        faithfulness_score = float(np.mean(scores)) if scores else 1.0
        
        return {
            "faithfulness_score": faithfulness_score,
            "unsupported_sentences": unsupported
        }
