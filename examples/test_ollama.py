import httpx
import asyncio

async def test():
    client = httpx.AsyncClient(timeout=30.0)
    try:
        r = await client.post(
            'http://host.docker.internal:11434/api/generate',
            json={'model': 'llama3.2:1b', 'prompt': 'test', 'stream': False}
        )
        print(f"Status: {r.status_code}")
        print(f"Response: {r.text[:300]}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await client.aclose()

asyncio.run(test())
