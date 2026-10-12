import pickle
from typing import List, Dict, Tuple
from rank_bm25 import BM25Okapi
from pathlib import Path

class BM25Index:
    def __init__(self):
        self.bm25 = None
        self.metadata = []
    
    def _tokenize(self, text: str) -> List[str]:
        return text.lower().split()
    
    def build_index(self, chunks: List[Dict]):
        self.metadata = chunks
        tokenized_corpus = [self._tokenize(chunk['text']) for chunk in chunks]
        self.bm25 = BM25Okapi(tokenized_corpus)
    
    def save(self, index_path: str):
        Path(index_path).mkdir(parents=True, exist_ok=True)
        with open(f"{index_path}/bm25.pkl", 'wb') as f:
            pickle.dump({'bm25': self.bm25, 'metadata': self.metadata}, f)
    
    def load(self, index_path: str):
        with open(f"{index_path}/bm25.pkl", 'rb') as f:
            data = pickle.load(f)
            self.bm25 = data['bm25']
            self.metadata = data['metadata']
    
    def search(self, query: str, top_k: int) -> List[Tuple[Dict, float]]:
        tokenized_query = self._tokenize(query)
        scores = self.bm25.get_scores(tokenized_query)
        
        top_indices = scores.argsort()[-top_k:][::-1]
        results = []
        for idx in top_indices:
            results.append((self.metadata[idx], float(scores[idx])))
        return results
