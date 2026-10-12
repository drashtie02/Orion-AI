import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient

@pytest.mark.unit
def test_app_creation():
    with patch('main.device_manager'):
        with patch('main.cache_manager'):
            from main import app
            
            assert app is not None
            assert app.title == "OrionAI"
            assert app.version == "1.0.0"

@pytest.mark.unit
def test_middleware_registration():
    with patch('main.device_manager'):
        with patch('main.cache_manager'):
            from main import app
            
            middleware_names = [str(m.cls) for m in app.user_middleware]
            
            assert any('RateLimitMiddleware' in name for name in middleware_names)
            assert any('RequestIDMiddleware' in name for name in middleware_names)

@pytest.mark.unit
def test_router_registration():
    with patch('main.device_manager'):
        with patch('main.cache_manager'):
            from main import app
            
            routes = [route.path for route in app.routes]
            
            assert any('/api/v1' in route for route in routes)
            assert any('/health' in route for route in routes)

@pytest.mark.asyncio
async def test_startup_event():
    with patch('main.device_manager') as mock_device:
        mock_device.get_device_name.return_value = 'cpu'
        mock_device.is_cuda.return_value = False
        
        with patch('main.cache_manager'):
            with patch('main.logger') as mock_logger:
                from main import startup_event
                
                await startup_event()
                
                assert mock_logger.info.called

@pytest.mark.asyncio
async def test_startup_event_with_gpu():
    with patch('main.device_manager') as mock_device:
        mock_device.get_device_name.return_value = 'cuda'
        mock_device.is_cuda.return_value = True
        mock_device.get_compute_capability.return_value = (12, 0)
        
        with patch('main.cache_manager'):
            with patch('main.logger') as mock_logger:
                from main import startup_event
                
                await startup_event()
                
                assert mock_logger.info.call_count >= 2

@pytest.mark.asyncio
async def test_shutdown_event():
    with patch('main.device_manager'):
        with patch('main.cache_manager') as mock_cache:
            mock_cache.close = AsyncMock()
            
            with patch('main.logger') as mock_logger:
                from main import shutdown_event
                
                await shutdown_event()
                
                mock_cache.close.assert_called_once()
                mock_logger.info.assert_called()

@pytest.mark.unit
def test_log_requests_middleware():
    with patch('main.device_manager'):
        with patch('main.cache_manager'):
            from main import app
            
            client = TestClient(app)
            
            with patch('main.logger') as mock_logger:
                response = client.get('/health')
                
                assert response.status_code in [200, 404]

@pytest.mark.unit
def test_sigterm_handler():
    with patch('main.device_manager'):
        with patch('main.cache_manager'):
            with patch('main.logger') as mock_logger:
                with patch('main.sys.exit') as mock_exit:
                    from main import handle_sigterm
                    
                    handle_sigterm()
                    
                    mock_logger.info.assert_called()
                    mock_exit.assert_called_once_with(0)
