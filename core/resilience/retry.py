import asyncio
import random
from typing import Callable, TypeVar, Optional, Type, Tuple
from functools import wraps
from dataclasses import dataclass
from core.logging import setup_logger

logger = setup_logger(__name__)

T = TypeVar('T')

@dataclass
class RetryConfig:
    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True

def is_transient_error(exception: Exception) -> bool:
    """Check if error is transient and should be retried"""
    transient_errors = (
        ConnectionError,
        TimeoutError,
        asyncio.TimeoutError,
    )
    
    if isinstance(exception, transient_errors):
        return True
    
    if hasattr(exception, 'status_code'):
        status = getattr(exception, 'status_code')
        return status >= 500 or status == 429
    
    error_msg = str(exception).lower()
    transient_keywords = ['timeout', 'connection', 'temporary', 'unavailable', 'overloaded']
    return any(keyword in error_msg for keyword in transient_keywords)

def retry_with_backoff(
    config: Optional[RetryConfig] = None,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
):
    """Decorator for async functions with exponential backoff retry logic"""
    if config is None:
        config = RetryConfig()
    
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            last_exception = None
            
            for attempt in range(config.max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == config.max_retries:
                        logger.error(
                            f"{func.__name__} failed after {config.max_retries} retries",
                            extra={'error': str(e), 'attempts': attempt + 1}
                        )
                        raise
                    
                    if not is_transient_error(e):
                        logger.warning(
                            f"{func.__name__} failed with non-transient error",
                            extra={'error': str(e)}
                        )
                        raise
                    
                    delay = min(
                        config.base_delay * (config.exponential_base ** attempt),
                        config.max_delay
                    )
                    
                    if config.jitter:
                        delay = delay * (0.5 + random.random() * 0.5)
                    
                    logger.warning(
                        f"{func.__name__} failed, retrying in {delay:.2f}s",
                        extra={
                            'attempt': attempt + 1,
                            'max_retries': config.max_retries,
                            'delay': delay,
                            'error': str(e)
                        }
                    )
                    
                    await asyncio.sleep(delay)
            
            raise last_exception
        
        return wrapper
    return decorator
