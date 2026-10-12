import pytest
from unittest.mock import Mock, AsyncMock, patch
from llm.router_async import LLMRouterAsync
from llm.base_model_async import BaseModel

@pytest.fixture
def mock_model_configs():
    return {
        'cheap_model': {
            'type': 'api',
            'model_name': 'llama2',
            'api_url': 'http://localhost:11434',
            'cost_per_1k_input': 0.0001,
            'cost_per_1k_output': 0.0002
        },
        'strong_model': {
            'type': 'api',
            'model_name': 'llama2-70b',
            'api_url': 'http://localhost:11434',
            'cost_per_1k_input': 0.001,
            'cost_per_1k_output': 0.002
        }
    }

@pytest.mark.asyncio
async def test_router_initialization_with_configs(mock_model_configs):
    with patch('llm.router_async.APIModel') as mock_api:
        mock_instance = Mock()
        mock_instance.model_name = 'llama2'
        mock_api.return_value = mock_instance
        
        router = LLMRouterAsync(mock_model_configs)
        
        assert len(router.models) == 2
        assert 'cheap_model' in router.models
        assert 'strong_model' in router.models

@pytest.mark.asyncio
async def test_router_initialization_without_configs():
    with patch('llm.router_async.config') as mock_config:
        mock_config.llm_type = 'api'
        mock_config.llm_api_url = 'http://localhost:11434'
        mock_config.llm_model = 'llama2'
        
        with patch('llm.router_async.APIModel') as mock_api:
            mock_instance = Mock()
            mock_instance.model_name = 'llama2'
            mock_api.return_value = mock_instance
            
            router = LLMRouterAsync()
            
            assert router.model is not None
            assert router.model_name == 'llama2'

@pytest.mark.asyncio
async def test_generate_with_specific_model(mock_model_configs):
    with patch('llm.router_async.APIModel') as mock_api:
        mock_instance = Mock()
        mock_instance.model_name = 'llama2'
        mock_instance.generate = AsyncMock(return_value={'text': 'response', 'tokens_input': 10, 'tokens_output': 20})
        mock_api.return_value = mock_instance
        
        router = LLMRouterAsync(mock_model_configs)
        result = await router.generate("test prompt", model_name='cheap_model')
        
        assert result['text'] == 'response'

@pytest.mark.asyncio
async def test_generate_with_default_model(mock_model_configs):
    with patch('llm.router_async.APIModel') as mock_api:
        mock_instance = Mock()
        mock_instance.model_name = 'llama2'
        mock_instance.generate = AsyncMock(return_value={'text': 'response', 'tokens_input': 10, 'tokens_output': 20})
        mock_api.return_value = mock_instance
        
        router = LLMRouterAsync(mock_model_configs)
        result = await router.generate("test prompt")
        
        assert result['text'] == 'response'

@pytest.mark.asyncio
async def test_generate_stream_with_specific_model(mock_model_configs):
    with patch('llm.router_async.APIModel') as mock_api:
        async def mock_stream(prompt):
            yield "chunk1"
            yield "chunk2"
        
        mock_instance = Mock()
        mock_instance.model_name = 'llama2'
        mock_instance.generate_stream = mock_stream
        mock_api.return_value = mock_instance
        
        router = LLMRouterAsync(mock_model_configs)
        chunks = []
        async for chunk in router.generate_stream("test prompt", model_name='cheap_model'):
            chunks.append(chunk)
        
        assert len(chunks) == 2
        assert chunks[0] == "chunk1"

@pytest.mark.asyncio
async def test_generate_stream_with_default_model(mock_model_configs):
    with patch('llm.router_async.APIModel') as mock_api:
        async def mock_stream(prompt):
            yield "chunk1"
        
        mock_instance = Mock()
        mock_instance.model_name = 'llama2'
        mock_instance.generate_stream = mock_stream
        mock_api.return_value = mock_instance
        
        router = LLMRouterAsync(mock_model_configs)
        chunks = []
        async for chunk in router.generate_stream("test prompt"):
            chunks.append(chunk)
        
        assert len(chunks) == 1

@pytest.mark.asyncio
async def test_get_model(mock_model_configs):
    with patch('llm.router_async.APIModel') as mock_api:
        mock_instance = Mock()
        mock_instance.model_name = 'llama2'
        mock_api.return_value = mock_instance
        
        router = LLMRouterAsync(mock_model_configs)
        model = router.get_model('cheap_model')
        
        assert model is not None

@pytest.mark.asyncio
async def test_get_nonexistent_model(mock_model_configs):
    with patch('llm.router_async.APIModel') as mock_api:
        mock_instance = Mock()
        mock_instance.model_name = 'llama2'
        mock_api.return_value = mock_instance
        
        router = LLMRouterAsync(mock_model_configs)
        model = router.get_model('nonexistent')
        
        assert model is None

@pytest.mark.asyncio
async def test_count_tokens(mock_model_configs):
    with patch('llm.router_async.APIModel') as mock_api:
        mock_instance = Mock()
        mock_instance.model_name = 'llama2'
        mock_instance.count_tokens = Mock(return_value=10)
        mock_api.return_value = mock_instance
        
        router = LLMRouterAsync(mock_model_configs)
        count = router.count_tokens("test text")
        
        assert count == 10

@pytest.mark.asyncio
async def test_close(mock_model_configs):
    with patch('llm.router_async.APIModel') as mock_api:
        mock_instance = Mock()
        mock_instance.model_name = 'llama2'
        mock_instance.close = AsyncMock()
        mock_api.return_value = mock_instance
        
        router = LLMRouterAsync(mock_model_configs)
        await router.close()
        
        assert mock_instance.close.called

@pytest.mark.asyncio
async def test_create_openai_model():
    config = {
        'type': 'openai',
        'model_name': 'gpt-4',
        'cost_per_1k_input': 0.03,
        'cost_per_1k_output': 0.06
    }
    
    with patch('llm.router_async.config') as mock_config:
        mock_config.openai_api_key = 'test-key'
        
        with patch('llm.router_async.OpenAIModel') as mock_openai:
            mock_instance = Mock()
            mock_instance.model_name = 'gpt-4'
            mock_openai.return_value = mock_instance
            
            router = LLMRouterAsync({'openai_model': config})
            
            assert 'openai_model' in router.models

@pytest.mark.asyncio
async def test_invalid_model_type():
    config = {
        'type': 'invalid',
        'model_name': 'test'
    }
    
    with pytest.raises(ValueError, match="Unknown model type"):
        router = LLMRouterAsync({'invalid_model': config})

@pytest.mark.asyncio
async def test_invalid_llm_type_initialization():
    with patch('llm.router_async.config') as mock_config:
        mock_config.llm_type = 'invalid'
        
        with pytest.raises(ValueError, match="Unknown LLM type"):
            router = LLMRouterAsync()
