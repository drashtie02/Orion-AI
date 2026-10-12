import pytest
import asyncio
from core.resilience import retry_with_backoff, RetryConfig

@pytest.mark.asyncio
async def test_retry_success_first_attempt():
    call_count = 0
    
    @retry_with_backoff(RetryConfig(max_retries=3))
    async def successful_func():
        nonlocal call_count
        call_count += 1
        return "success"
    
    result = await successful_func()
    assert result == "success"
    assert call_count == 1

@pytest.mark.asyncio
async def test_retry_success_after_failures():
    call_count = 0
    
    @retry_with_backoff(RetryConfig(max_retries=3, base_delay=0.1))
    async def eventually_successful():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise ConnectionError("Temporary failure")
        return "success"
    
    result = await eventually_successful()
    assert result == "success"
    assert call_count == 3

@pytest.mark.asyncio
async def test_retry_exhausted():
    call_count = 0
    
    @retry_with_backoff(RetryConfig(max_retries=2, base_delay=0.1))
    async def always_fails():
        nonlocal call_count
        call_count += 1
        raise ConnectionError("Persistent failure")
    
    with pytest.raises(ConnectionError):
        await always_fails()
    
    assert call_count == 3

@pytest.mark.asyncio
async def test_retry_non_transient_error():
    call_count = 0
    
    @retry_with_backoff(RetryConfig(max_retries=3))
    async def client_error():
        nonlocal call_count
        call_count += 1
        error = Exception("Client error")
        error.status_code = 400
        raise error
    
    with pytest.raises(Exception):
        await client_error()
    
    assert call_count == 1

@pytest.mark.asyncio
async def test_retry_exponential_backoff():
    delays = []
    
    @retry_with_backoff(RetryConfig(max_retries=3, base_delay=1.0, jitter=False))
    async def track_delays():
        delays.append(asyncio.get_event_loop().time())
        raise ConnectionError("Retry me")
    
    with pytest.raises(ConnectionError):
        await track_delays()
    
    assert len(delays) == 4

@pytest.mark.asyncio
async def test_retry_with_timeout_error():
    call_count = 0
    
    @retry_with_backoff(RetryConfig(max_retries=2, base_delay=0.1))
    async def timeout_error():
        nonlocal call_count
        call_count += 1
        raise TimeoutError("Request timeout")
    
    with pytest.raises(TimeoutError):
        await timeout_error()
    
    assert call_count == 3

@pytest.mark.asyncio
async def test_retry_with_rate_limit_error():
    call_count = 0
    
    @retry_with_backoff(RetryConfig(max_retries=2, base_delay=0.1))
    async def rate_limit_error():
        nonlocal call_count
        call_count += 1
        error = Exception("Rate limited")
        error.status_code = 429
        raise error
    
    with pytest.raises(Exception):
        await rate_limit_error()
    
    assert call_count == 3

@pytest.mark.asyncio
async def test_retry_with_max_delay():
    call_count = 0
    
    @retry_with_backoff(RetryConfig(max_retries=5, base_delay=10.0, max_delay=2.0))
    async def test_func():
        nonlocal call_count
        call_count += 1
        raise ConnectionError("Retry")
    
    with pytest.raises(ConnectionError):
        await test_func()
    
    assert call_count == 6

@pytest.mark.asyncio
async def test_retry_with_jitter():
    call_count = 0
    
    @retry_with_backoff(RetryConfig(max_retries=2, base_delay=0.1, jitter=True))
    async def test_func():
        nonlocal call_count
        call_count += 1
        raise ConnectionError("Retry")
    
    with pytest.raises(ConnectionError):
        await test_func()
    
    assert call_count == 3

@pytest.mark.asyncio
async def test_retry_with_zero_retries():
    call_count = 0
    
    @retry_with_backoff(RetryConfig(max_retries=0))
    async def test_func():
        nonlocal call_count
        call_count += 1
        raise ConnectionError("Fail")
    
    with pytest.raises(ConnectionError):
        await test_func()
    
    assert call_count == 1
