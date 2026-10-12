from fastapi import FastAPI, Request
from api.routes import router
from api.health import router as health_router
from core.device import device_manager
from core.logging import setup_logger
from core.middleware import RateLimitMiddleware, RequestIDMiddleware
from core.cache import cache_manager
import time
import signal
import sys

logger = setup_logger(__name__)

app = FastAPI(
    title="OrionAI",
    version="1.0.0",
    description="Production-grade Hybrid RAG system with intelligent model routing"
)

app.add_middleware(RateLimitMiddleware)
app.add_middleware(RequestIDMiddleware)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    latency = time.time() - start_time
    
    logger.info(
        f"{request.method} {request.url.path}",
        extra={
            'endpoint': request.url.path,
            'latency': round(latency, 4)
        }
    )
    return response

app.include_router(router, prefix="/api/v1")
app.include_router(health_router)

@app.on_event("startup")
async def startup_event():
    logger.info(f"OrionAI v1.0.0 starting")
    logger.info(f"Device: {device_manager.get_device_name()}")
    if device_manager.is_cuda():
        capability = device_manager.get_compute_capability()
        logger.info(f"GPU compute capability: sm_{capability[0]}{capability[1]}")

@app.on_event("shutdown")
async def shutdown_event():
    await cache_manager.close()
    logger.info("OrionAI shutdown complete")

def handle_sigterm(*args):
    logger.info("SIGTERM received, initiating graceful shutdown")
    sys.exit(0)

signal.signal(signal.SIGTERM, handle_sigterm)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8011)
