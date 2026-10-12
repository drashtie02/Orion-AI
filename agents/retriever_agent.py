from typing import Dict
from .base_agent import BaseAgent
import time
import logging

logger = logging.getLogger(__name__)

class RetrieverAgent(BaseAgent):
    def __init__(self, retriever):
        self.retriever = retriever
    
    def execute(self, input_data: Dict) -> Dict:
        query = input_data['query']
        top_k = input_data.get('top_k', 5)
        
        start = time.time()
        results = self.retriever.search(query, top_k)
        latency = time.time() - start
        
        logger.info(f"Retrieved {len(results)} chunks in {latency*1000:.0f}ms")
        
        return {
            "output": {
                "retrieved_chunks": results,
                "retrieval_scores": [r['hybrid_score'] for r in results]
            },
            "metadata": {
                "agent": "retriever",
                "latency": latency,
                "num_chunks": len(results)
            }
        }
