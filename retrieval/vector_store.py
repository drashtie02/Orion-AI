import json
import numpy as np
import faiss
from pathlib import Path
from typing import List, Dict, Tuple
from sentence_transformers import SentenceTransformer
from core.config import config
from core.device import device_manager
from retrieval.api_embedding import APIEmbeddingModel

class VectorStore:
    def __init__(self):
        if config.embedding_type == 'api' and config.embedding_api_url:
            self.model = APIEmbeddingModel(config.embedding_api_url, config.embedding_model)
        else:
            device = device_manager.get_device()
            self.model = SentenceTransformer(config.embedding_model, device=device, trust_remote_code=True)
        
        self.index = None
        self.metadata = []
        self.dimension = self.model.get_sentence_embedding_dimension()
        self.batch_size = config.gpu_batch_size if device_manager.is_cuda() else config.cpu_batch_size
        
    def build_index(self, chunks: List[Dict]):
        texts = [chunk['text'] for chunk in chunks]
        embeddings = self.model.encode(texts, batch_size=self.batch_size, show_progress_bar=False, convert_to_numpy=True)
        
        self.index = faiss.IndexFlatIP(self.dimension)
        faiss.normalize_L2(embeddings)
        self.index.add(embeddings)
        self.metadata = chunks
    
    def save(self, index_path: str):
        Path(index_path).mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, f"{index_path}/faiss.index")
        with open(f"{index_path}/metadata.json", 'w') as f:
            json.dump(self.metadata, f)
    
    def load(self, index_path: str):
        self.index = faiss.read_index(f"{index_path}/faiss.index")
        with open(f"{index_path}/metadata.json", 'r') as f:
            self.metadata = json.load(f)
    
    def search(self, query: str, top_k: int) -> List[Tuple[Dict, float]]:
        query_embedding = self.model.encode([query], convert_to_numpy=True)
        faiss.normalize_L2(query_embedding)
        
        scores, indices = self.index.search(query_embedding, top_k)
        results = []
        for idx, score in zip(indices[0], scores[0]):
            if idx < len(self.metadata):
                results.append((self.metadata[idx], float(score)))
        return results
    
    def embed_query(self, query: str) -> np.ndarray:
        return self.model.encode([query], convert_to_numpy=True)[0]
