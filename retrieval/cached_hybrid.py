from typing import List, Dict
from retrieval.hybrid import HybridRetriever as BaseHybridRetriever
from core.cache import cache_manager
import json

class CachedHybridRetriever(BaseHybridRetriever):
    async def search_cached(self, query: str, top_k: int) -> List[Dict]:
        cache_key = json.dumps({'query': query, 'top_k': top_k, 'alpha': self.alpha}, sort_keys=True)
        
        cached_result = await cache_manager.get('retrieval', cache_key)
        if cached_result:
            return cached_result
        
        results = self.search(query, top_k)
        
        await cache_manager.set('retrieval', cache_key, results)
        
        return results
