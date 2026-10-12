# OrionAI Examples

This directory contains example scripts and test utilities for OrionAI.

## Contents

### `load_test.py`
Simple load testing script for measuring OrionAI performance.

**Usage:**
```bash
python examples/load_test.py
```

**Features:**
- Concurrent request testing
- Latency measurements
- Success rate tracking
- Multiple test scenarios

### `test_ollama.py`
Quick test script for validating Ollama connectivity.

**Usage:**
```bash
python examples/test_ollama.py
```

### `api_test_data.json`
Comprehensive API test cases and examples.

**Contents:**
- Endpoint documentation
- Test case definitions
- Expected responses
- curl examples
- Python examples

## Running Examples

### Prerequisites

Ensure OrionAI is running:
```bash
# Local
python main.py

# Docker
docker-compose up

# Kubernetes
kubectl port-forward -n orionai svc/orionai-service 8011:8011
```

### Load Testing

```bash
# Basic load test
python examples/load_test.py

# For production load testing, use k6 or Locust:
cd load-testing
k6 run k6-script.js
```

### API Testing

```bash
# Health check
curl http://localhost:8011/health

# Basic query
curl -X POST http://localhost:8011/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Who is Iron Man?", "top_k": 5}'

# Streaming query
curl -X POST http://localhost:8011/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Who is Iron Man?", "stream": true}'
```

## Notes

These examples are for development and testing purposes. For production load testing, use the tools in the `load-testing/` directory.
