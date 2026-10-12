import pytest
from unittest.mock import Mock, AsyncMock, patch
from llm.api_model_async import APIModel
from llm.base_model_async import BaseModel

@pytest.mark.asyncio
async def test_api_model_initialization():
    model = APIModel('http://localhost:11434', 'llama2', 0.001, 0.002)
    assert model.api_url == 'http://localhost:11434'
    assert model.model_name == 'llama2'

@pytest.mark.asyncio
async def test_api_model_count_tokens():
    model = APIModel('http://localhost:11434', 'llama2')
    count = model.count_tokens('test text')
    assert count > 0

@pytest.mark.asyncio
async def test_api_model_generate_error():
    model = APIModel('http://localhost:11434', 'llama2')
    
    with patch('httpx.AsyncClient.post', side_effect=Exception('Connection error')):
        with pytest.raises(Exception):
            await model.generate('test prompt')

@pytest.mark.asyncio
async def test_api_model_close():
    model = APIModel('http://localhost:11434', 'llama2')
    await model.close()
    assert model._client is None
