import os
import time
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from redis import asyncio as aioredis
import logging

logger = logging.getLogger(__name__)

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.enabled = os.getenv('RATE_LIMIT_ENABLED', 'true').lower() == 'true'
        self.requests_limit = int(os.getenv('RATE_LIMIT_REQUESTS', '100'))
        self.window_seconds = int(os.getenv('RATE_LIMIT_WINDOW_SECONDS', '60'))
        
        redis_host = os.getenv('REDIS_HOST', 'localhost')
        redis_port = int(os.getenv('REDIS_PORT', '6379'))
        redis_db = int(os.getenv('REDIS_DB', '0'))
        
        self.redis_client = None
        if self.enabled:
            try:
                self.redis_client = aioredis.Redis(
                    host=redis_host,
                    port=redis_port,
                    db=redis_db,
                    decode_responses=True
                )
                logger.info(f"Rate limiting enabled: {self.requests_limit} req/{self.window_seconds}s")
            except Exception as e:
                logger.warning(f"Redis unavailable for rate limiting: {e}")
                self.enabled = False
    
    async def dispatch(self, request: Request, call_next):
        if not self.enabled or not self.redis_client:
            return await call_next(request)
        
        client_ip = request.client.host
        key = f"rate_limit:{client_ip}"
        
        try:
            current = await self.redis_client.get(key)
            
            if current is None:
                await self.redis_client.setex(key, self.window_seconds, 1)
                request_count = 1
            else:
                request_count = int(current)
                if request_count >= self.requests_limit:
                    ttl = await self.redis_client.ttl(key)
                    return JSONResponse(
                        status_code=429,
                        content={
                            "error": "Rate limit exceeded",
                            "retry_after": ttl
                        },
                        headers={"Retry-After": str(ttl)}
                    )
                await self.redis_client.incr(key)
                request_count += 1
            
            response = await call_next(request)
            response.headers["X-RateLimit-Limit"] = str(self.requests_limit)
            response.headers["X-RateLimit-Remaining"] = str(max(0, self.requests_limit - request_count))
            response.headers["X-RateLimit-Reset"] = str(int(time.time()) + self.window_seconds)
            return response
            
        except Exception as e:
            logger.error(f"Rate limit check failed: {e}")
            return await call_next(request)
