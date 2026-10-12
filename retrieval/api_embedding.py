import numpy as np
import requests
from typing import List

class APIEmbeddingModel:
    def __init__(self, api_url: str, model_name: str):
        self.api_url = api_url
        self.model_name = model_name
        self.dimension = 384
    
    def encode(self, texts: List[str], batch_size: int = 32, show_progress_bar: bool = False, convert_to_numpy: bool = True):
        embeddings = []
        for text in texts:
            response = requests.post(
                self.api_url,
                json={"model": self.model_name, "prompt": text}
            )
            if response.status_code == 200:
                embedding = response.json().get('embedding', [])
                embeddings.append(embedding)
            else:
                embeddings.append([0.0] * self.dimension)
        
        if convert_to_numpy:
            return np.array(embeddings, dtype=np.float32)
        return embeddings
    
    def get_sentence_embedding_dimension(self):
        return self.dimension
