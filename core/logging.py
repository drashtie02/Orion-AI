import logging
import sys
import json
import os
from datetime import datetime
from typing import Any, Dict
from core.middleware.request_id import get_request_id

class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
        }
        
        request_id = get_request_id()
        if request_id:
            log_data['request_id'] = request_id
        
        if hasattr(record, 'endpoint'):
            log_data['endpoint'] = record.endpoint
        if hasattr(record, 'latency'):
            log_data['latency'] = record.latency
        if hasattr(record, 'model_used'):
            log_data['model_used'] = record.model_used
        if hasattr(record, 'cache_hit'):
            log_data['cache_hit'] = record.cache_hit
        if hasattr(record, 'error_type'):
            log_data['error_type'] = record.error_type
        
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)

def setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    log_level = os.getenv('LOG_LEVEL', 'INFO')
    environment = os.getenv('ENVIRONMENT', 'production')
    
    logger.setLevel(getattr(logging, log_level.upper()))
    logger.handlers.clear()
    
    handler = logging.StreamHandler(sys.stdout)
    
    if environment == 'production':
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
