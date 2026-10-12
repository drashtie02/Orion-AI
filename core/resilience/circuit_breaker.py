import asyncio
import time
from enum import Enum
from typing import Callable, TypeVar, Optional
from functools import wraps
from dataclasses import dataclass
from collections import deque
from core.logging import setup_logger

logger = setup_logger(__name__)

T = TypeVar('T')

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

@dataclass
class CircuitBreakerConfig:
    failure_threshold: int = 5
    recovery_timeout: float = 60.0
    window_size: int = 10
    half_open_max_calls: int = 1

class CircuitBreaker:
    def __init__(self, name: str, config: Optional[CircuitBreakerConfig] = None):
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._last_failure_time: Optional[float] = None
        self._failure_window = deque(maxlen=self.config.window_size)
        self._half_open_calls = 0
        self._lock = asyncio.Lock()
    
    @property
    def state(self) -> CircuitState:
        return self._state
    
    async def _transition_to(self, new_state: CircuitState):
        if self._state != new_state:
            old_state = self._state
            self._state = new_state
            logger.info(
                f"Circuit breaker '{self.name}' state transition",
                extra={
                    'circuit_breaker': self.name,
                    'old_state': old_state.value,
                    'new_state': new_state.value
                }
            )
    
    async def _record_success(self):
        async with self._lock:
            if self._state == CircuitState.HALF_OPEN:
                await self._transition_to(CircuitState.CLOSED)
                self._failure_count = 0
                self._failure_window.clear()
                self._half_open_calls = 0
                logger.info(f"Circuit breaker '{self.name}' recovered")
    
    async def _record_failure(self):
        async with self._lock:
            self._failure_count += 1
            self._last_failure_time = time.time()
            self._failure_window.append(time.time())
            
            if self._state == CircuitState.HALF_OPEN:
                await self._transition_to(CircuitState.OPEN)
                self._half_open_calls = 0
            elif self._state == CircuitState.CLOSED:
                if len(self._failure_window) >= self.config.failure_threshold:
                    await self._transition_to(CircuitState.OPEN)
    
    async def _check_and_update_state(self):
        async with self._lock:
            if self._state == CircuitState.OPEN:
                if self._last_failure_time and \
                   (time.time() - self._last_failure_time) >= self.config.recovery_timeout:
                    await self._transition_to(CircuitState.HALF_OPEN)
                    self._half_open_calls = 0
    
    async def call(self, func: Callable[..., T], *args, **kwargs) -> T:
        await self._check_and_update_state()
        
        if self._state == CircuitState.OPEN:
            raise CircuitBreakerOpenError(f"Circuit breaker '{self.name}' is OPEN")
        
        if self._state == CircuitState.HALF_OPEN:
            async with self._lock:
                if self._half_open_calls >= self.config.half_open_max_calls:
                    raise CircuitBreakerOpenError(
                        f"Circuit breaker '{self.name}' is HALF_OPEN and at max calls"
                    )
                self._half_open_calls += 1
        
        try:
            result = await func(*args, **kwargs)
            await self._record_success()
            return result
        except Exception as e:
            await self._record_failure()
            raise
    
    def __call__(self, func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            return await self.call(func, *args, **kwargs)
        return wrapper

class CircuitBreakerOpenError(Exception):
    pass
