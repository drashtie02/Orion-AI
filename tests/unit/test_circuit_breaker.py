import pytest
import asyncio
from core.resilience import CircuitBreaker, CircuitState, CircuitBreakerOpenError, CircuitBreakerConfig

@pytest.mark.asyncio
async def test_circuit_breaker_closed_state():
    cb = CircuitBreaker("test", CircuitBreakerConfig(failure_threshold=3))
    
    async def successful_call():
        return "success"
    
    result = await cb.call(successful_call)
    assert result == "success"
    assert cb.state == CircuitState.CLOSED

@pytest.mark.asyncio
async def test_circuit_breaker_opens_after_failures():
    cb = CircuitBreaker("test", CircuitBreakerConfig(failure_threshold=3, window_size=5))
    
    async def failing_call():
        raise Exception("Failure")
    
    for _ in range(3):
        with pytest.raises(Exception):
            await cb.call(failing_call)
    
    assert cb.state == CircuitState.OPEN

@pytest.mark.asyncio
async def test_circuit_breaker_rejects_when_open():
    cb = CircuitBreaker("test", CircuitBreakerConfig(failure_threshold=2))
    
    async def failing_call():
        raise Exception("Failure")
    
    for _ in range(2):
        with pytest.raises(Exception):
            await cb.call(failing_call)
    
    assert cb.state == CircuitState.OPEN
    
    async def any_call():
        return "success"
    
    with pytest.raises(CircuitBreakerOpenError):
        await cb.call(any_call)

@pytest.mark.asyncio
async def test_circuit_breaker_half_open_recovery():
    cb = CircuitBreaker("test", CircuitBreakerConfig(
        failure_threshold=2,
        recovery_timeout=0.5
    ))
    
    async def failing_call():
        raise Exception("Failure")
    
    for _ in range(2):
        with pytest.raises(Exception):
            await cb.call(failing_call)
    
    assert cb.state == CircuitState.OPEN
    
    await asyncio.sleep(0.6)
    
    async def successful_call():
        return "success"
    
    result = await cb.call(successful_call)
    assert result == "success"
    assert cb.state == CircuitState.CLOSED

@pytest.mark.asyncio
async def test_circuit_breaker_half_open_failure():
    cb = CircuitBreaker("test", CircuitBreakerConfig(
        failure_threshold=2,
        recovery_timeout=0.5
    ))
    
    async def failing_call():
        raise Exception("Failure")
    
    for _ in range(2):
        with pytest.raises(Exception):
            await cb.call(failing_call)
    
    await asyncio.sleep(0.6)
    
    with pytest.raises(Exception):
        await cb.call(failing_call)
    
    assert cb.state == CircuitState.OPEN

@pytest.mark.asyncio
async def test_circuit_breaker_window_size():
    cb = CircuitBreaker("test", CircuitBreakerConfig(
        failure_threshold=3,
        window_size=2
    ))
    
    async def failing_call():
        raise Exception("Failure")
    
    async def successful_call():
        return "success"
    
    with pytest.raises(Exception):
        await cb.call(failing_call)
    
    await cb.call(successful_call)
    
    with pytest.raises(Exception):
        await cb.call(failing_call)
    
    assert cb.state == CircuitState.CLOSED

@pytest.mark.asyncio
async def test_circuit_breaker_multiple_open_attempts():
    cb = CircuitBreaker("test", CircuitBreakerConfig(
        failure_threshold=2,
        recovery_timeout=10.0
    ))
    
    async def failing_call():
        raise Exception("Failure")
    
    for _ in range(2):
        with pytest.raises(Exception):
            await cb.call(failing_call)
    
    assert cb.state == CircuitState.OPEN
    
    for _ in range(5):
        with pytest.raises(CircuitBreakerOpenError):
            await cb.call(failing_call)
    
    assert cb.state == CircuitState.OPEN

@pytest.mark.asyncio
async def test_circuit_breaker_name():
    cb = CircuitBreaker("test_service", CircuitBreakerConfig(failure_threshold=3))
    
    assert cb.name == "test_service"

@pytest.mark.asyncio
async def test_circuit_breaker_config_validation():
    config = CircuitBreakerConfig(
        failure_threshold=5,
        recovery_timeout=60.0,
        window_size=10
    )
    
    assert config.failure_threshold == 5
    assert config.recovery_timeout == 60.0
    assert config.window_size == 10
