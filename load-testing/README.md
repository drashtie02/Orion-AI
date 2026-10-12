# Load Testing OrionAI

This directory contains load testing scripts for OrionAI using k6 and Locust.

## Prerequisites

### k6
```bash
# macOS
brew install k6

# Linux
sudo gpg -k
sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
sudo apt-get update
sudo apt-get install k6

# Docker
docker pull grafana/k6
```

### Locust
```bash
pip install locust
```

## Running k6 Tests

### Basic Test
```bash
k6 run k6-script.js
```

### Against Kubernetes Service
```bash
# Port forward to local
kubectl port-forward -n orionai svc/orionai-service 8011:8011

# Run test
BASE_URL=http://localhost:8011 k6 run k6-script.js
```

### Against Ingress
```bash
BASE_URL=https://orionai.example.com API_KEY=your_key k6 run k6-script.js
```

### Custom Configuration
```bash
# Adjust VUs and duration
k6 run --vus 100 --duration 10m k6-script.js

# Save results
k6 run --out json=results.json k6-script.js
```

### Docker
```bash
docker run --rm -i grafana/k6 run - <k6-script.js
```

## Running Locust Tests

### Basic Test
```bash
locust -f locustfile.py --host=http://localhost:8011
```

### Headless Mode
```bash
locust -f locustfile.py \
  --host=http://localhost:8011 \
  --users 100 \
  --spawn-rate 10 \
  --run-time 10m \
  --headless
```

### With API Key
```bash
API_KEY=your_key locust -f locustfile.py --host=http://localhost:8011
```

### Web UI
```bash
locust -f locustfile.py --host=http://localhost:8011
# Open http://localhost:8089
```

## Test Stages (k6)

The k6 script includes the following stages:

1. **Ramp-up (2m)**: 0 → 10 users
2. **Load increase (5m)**: 10 → 50 users
3. **Spike (3m)**: 50 → 100 users
4. **Sustained load (5m)**: 100 users
5. **Ramp-down (2m)**: 100 → 50 users
6. **Cool-down (2m)**: 50 → 0 users

Total duration: ~19 minutes

## Metrics

### k6 Metrics
- **http_req_duration**: Request latency (p50, p90, p95, p99)
- **http_reqs**: Total requests and request rate
- **http_req_failed**: Failed request percentage
- **errors**: Custom error rate
- **query_latency**: Custom query latency metric

### Locust Metrics
- **Requests/s**: Throughput
- **Response time**: p50, p95, p99
- **Failures**: Error count and percentage
- **Users**: Concurrent users

## Thresholds

k6 test will fail if:
- p95 latency > 2000ms
- p99 latency > 5000ms
- Error rate > 5%
- HTTP failure rate > 5%

## Results

Results are saved to:
- k6: `load-testing/results.json`
- Locust: Console output or web UI

## Example Output

```
Test Summary:
  Duration: 1140s
  Iterations: 45230
  VUs: 100

HTTP Metrics:
  Requests: 45230
  Request Rate: 39.68/s
  Failed Requests: 0.12%

Latency:
  Avg: 1234.56ms
  Min: 234.12ms
  Max: 4567.89ms
  p50: 1123.45ms
  p90: 1789.23ms
  p95: 2012.34ms
  p99: 3456.78ms

Error Rate: 0.12%
```

## Interpreting Results

### Good Performance
- p95 < 2000ms
- p99 < 5000ms
- Error rate < 1%
- Request rate > 30/s

### Needs Optimization
- p95 > 2000ms
- p99 > 5000ms
- Error rate > 1%
- Request rate < 20/s

## Tuning Recommendations

If performance is poor:

1. **Increase replicas**: Edit HPA maxReplicas
2. **Increase resources**: Adjust CPU/memory limits
3. **Enable caching**: Ensure Redis is enabled
4. **Optimize queries**: Review retrieval configuration
5. **Scale Redis**: Add Redis replicas or use external Redis cluster
6. **Review logs**: Check for bottlenecks in application logs

## Monitoring During Tests

```bash
# Watch pod metrics
kubectl top pods -n orionai --watch

# Watch HPA
kubectl get hpa -n orionai --watch

# Stream logs
kubectl logs -n orionai -l app=orionai -f
```
