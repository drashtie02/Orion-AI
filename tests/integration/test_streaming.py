import pytest
import httpx
import asyncio
import json

@pytest.mark.asyncio
async def test_streaming_response():
    async with httpx.AsyncClient(timeout=30.0) as client:
        async with client.stream(
            'POST',
            'http://localhost:8011/api/v1/query',
            json={"query": "What is machine learning?", "stream": True}
        ) as response:
            assert response.status_code == 200
            
            chunks_received = []
            async for line in response.aiter_lines():
                if line.startswith('data: '):
                    data = json.loads(line[6:])
                    chunks_received.append(data)
            
            assert len(chunks_received) > 0
            assert chunks_received[0]['type'] == 'start'
            assert chunks_received[-1]['type'] == 'end'

@pytest.mark.asyncio
async def test_streaming_client_disconnect():
    async with httpx.AsyncClient(timeout=30.0) as client:
        async with client.stream(
            'POST',
            'http://localhost:8011/api/v1/query',
            json={"query": "What is machine learning?", "stream": True}
        ) as response:
            count = 0
            async for line in response.aiter_lines():
                count += 1
                if count >= 3:
                    break
            
            assert count >= 3

@pytest.mark.asyncio
async def test_non_streaming_response():
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            'http://localhost:8011/api/v1/query',
            json={"query": "What is machine learning?", "stream": False}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert 'answer' in data
        assert 'sources' in data
        assert 'request_id' in data

@pytest.mark.asyncio
async def test_concurrent_streaming():
    async def stream_request():
        async with httpx.AsyncClient(timeout=30.0) as client:
            async with client.stream(
                'POST',
                'http://localhost:8011/api/v1/query',
                json={"query": "What is machine learning?", "stream": True}
            ) as response:
                chunks = []
                async for line in response.aiter_lines():
                    if line.startswith('data: '):
                        chunks.append(json.loads(line[6:]))
                return len(chunks)
    
    results = await asyncio.gather(*[stream_request() for _ in range(5)])
    
    assert all(r > 0 for r in results)
