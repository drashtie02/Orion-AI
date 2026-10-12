import os
import json
import hashlib
from typing import Optional, Any
from redis import asyncio as aioredis
from redis.asyncio import ConnectionPool
import logging

logger = logging.getLogger(__name__)

class CacheManager:
    def __init__(self):
        self.enabled = os.getenv('REDIS_ENABLED', 'false').lower() == 'true'
        self.host = os.getenv('REDIS_HOST', 'localhost')
        self.port = int(os.getenv('REDIS_PORT', '6379'))
        self.db = int(os.getenv('REDIS_DB', '0'))
        self.ttl = int(os.getenv('CACHE_TTL', '3600'))
        self.pool: Optional[ConnectionPool] = None
        self.client: Optional[aioredis.Redis] = None
        
        if self.enabled:
            try:
                self.pool = ConnectionPool(
                    host=self.host,
                    port=self.port,
                    db=self.db,
                    decode_responses=True,
                    max_connections=10
                )
                self.client = aioredis.Redis(connection_pool=self.pool)
                logger.info(f"Redis cache enabled: {self.host}:{self.port}/{self.db}")
            except Exception as e:
                logger.warning(f"Redis connection failed, caching disabled: {e}")
                self.enabled = False
    
    def _generate_key(self, prefix: str, data: str) -> str:
        hash_obj = hashlib.sha256(data.encode())
        return f"{prefix}:{hash_obj.hexdigest()}"
    
    async def get(self, prefix: str, key: str) -> Optional[Any]:
        if not self.enabled or not self.client:
            return None
        
        try:
            cache_key = self._generate_key(prefix, key)
            value = await self.client.get(cache_key)
            if value:
                return json.loads(value)
        except Exception as e:
            logger.error(f"Cache get error: {e}")
        return None
    
    async def set(self, prefix: str, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        if not self.enabled or not self.client:
            return False
        
        try:
            cache_key = self._generate_key(prefix, key)
            ttl = ttl or self.ttl
            await self.client.setex(cache_key, ttl, json.dumps(value))
            return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    async def close(self):
        if self.client:
            await self.client.close()
        if self.pool:
            await self.pool.disconnect()

cache_manager = CacheManager()
