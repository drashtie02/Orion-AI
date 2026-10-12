import pytest
import json
import logging
from unittest.mock import patch
from core.logging import setup_logger, JSONFormatter

@pytest.mark.unit
class TestLogging:
    def test_json_formatter_basic(self):
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name='test',
            level=logging.INFO,
            pathname='',
            lineno=0,
            msg='Test message',
            args=(),
            exc_info=None
        )
        
        output = formatter.format(record)
        data = json.loads(output)
        
        assert data['level'] == 'INFO'
        assert data['message'] == 'Test message'
        assert 'timestamp' in data
    
    def test_json_formatter_with_extras(self):
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name='test',
            level=logging.ERROR,
            pathname='',
            lineno=0,
            msg='Error occurred',
            args=(),
            exc_info=None
        )
        record.endpoint = '/api/v1/query'
        record.latency = 1.234
        record.error_type = 'timeout'
        
        output = formatter.format(record)
        data = json.loads(output)
        
        assert data['endpoint'] == '/api/v1/query'
        assert data['latency'] == 1.234
        assert data['error_type'] == 'timeout'
    
    def test_setup_logger_production(self):
        with patch.dict('os.environ', {'ENVIRONMENT': 'production', 'LOG_LEVEL': 'INFO'}):
            logger = setup_logger('test_logger')
            
            assert logger.level == logging.INFO
            assert len(logger.handlers) > 0
            assert isinstance(logger.handlers[0].formatter, JSONFormatter)
    
    def test_setup_logger_development(self):
        with patch.dict('os.environ', {'ENVIRONMENT': 'development', 'LOG_LEVEL': 'DEBUG'}):
            logger = setup_logger('test_logger_dev')
            
            assert logger.level == logging.DEBUG
            assert len(logger.handlers) > 0
