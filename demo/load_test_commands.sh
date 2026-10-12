#!/bin/bash

# OrionAI Load Testing Commands
# Commands for running load tests during demo

set -e

BASE_URL="${BASE_URL:-http://localhost:8011}"

echo "==================================="
echo "OrionAI Load Testing"
echo "==================================="
echo ""

# Check if k6 is installed
if ! command -v k6 &> /dev/null; then
    echo "k6 not found. Install with:"
    echo "  macOS: brew install k6"
    echo "  Linux: sudo apt install k6"
    echo "  Windows: choco install k6"
    exit 1
fi

# 1. Quick Load Test (30 seconds)
echo "[1] Quick Load Test (30s, 10 users)"
k6 run --duration 30s --vus 10 - <<EOF
import http from 'k6/http';
import { check, sleep } from 'k6';

export default function () {
  const url = '${BASE_URL}/api/v1/query';
  const payload = JSON.stringify({
    query: 'What is machine learning?',
    top_k: 5
  });
  const params = {
    headers: {
      'Content-Type': 'application/json',
    },
  };

  const res = http.post(url, payload, params);
  check(res, {
    'status is 200': (r) => r.status === 200,
    'response time < 2000ms': (r) => r.timings.duration < 2000,
  });

  sleep(1);
}
EOF
echo ""

# 2. Ramp-up Load Test (2 minutes)
echo "[2] Ramp-up Load Test (2min, 0→50 users)"
k6 run --stage 30s:10 --stage 30s:30 --stage 30s:50 --stage 30s:0 - <<EOF
import http from 'k6/http';
import { check, sleep } from 'k6';

const queries = [
  'What is machine learning?',
  'Explain neural networks',
  'What is deep learning?',
  'Compare supervised and unsupervised learning',
  'What is transfer learning?'
];

export default function () {
  const query = queries[Math.floor(Math.random() * queries.length)];
  const url = '${BASE_URL}/api/v1/query';
  const payload = JSON.stringify({
    query: query,
    top_k: 5
  });
  const params = {
    headers: {
      'Content-Type': 'application/json',
    },
  };

  const res = http.post(url, payload, params);
  check(res, {
    'status is 200': (r) => r.status === 200,
    'response time < 3000ms': (r) => r.timings.duration < 3000,
  });

  sleep(Math.random() * 2 + 1);
}
EOF
echo ""

# 3. Stress Test (High concurrency)
echo "[3] Stress Test (1min, 100 users)"
k6 run --duration 60s --vus 100 - <<EOF
import http from 'k6/http';
import { check } from 'k6';

export default function () {
  const url = '${BASE_URL}/api/v1/query';
  const payload = JSON.stringify({
    query: 'What is artificial intelligence?',
    top_k: 3
  });
  const params = {
    headers: {
      'Content-Type': 'application/json',
    },
  };

  const res = http.post(url, payload, params);
  check(res, {
    'status is 200 or 429': (r) => r.status === 200 || r.status === 429,
  });
}
EOF
echo ""

# 4. Locust Alternative (if installed)
if command -v locust &> /dev/null; then
    echo "[4] Locust Load Test (Alternative)"
    echo "Run: locust -f load-testing/locustfile.py --host=${BASE_URL} --headless --users 50 --spawn-rate 5 --run-time 60s"
else
    echo "[4] Locust not installed (optional)"
    echo "Install: pip install locust"
fi
echo ""

# 5. Kubernetes Monitoring (if applicable)
if command -v kubectl &> /dev/null; then
    echo "[5] Kubernetes Monitoring Commands"
    echo ""
    echo "Watch pods:"
    echo "  kubectl get pods -n orionai -w"
    echo ""
    echo "Watch HPA:"
    echo "  kubectl get hpa -n orionai --watch"
    echo ""
    echo "Resource usage:"
    echo "  kubectl top pods -n orionai"
    echo ""
    echo "Logs:"
    echo "  kubectl logs -n orionai -l app=orionai -f"
fi

echo ""
echo "==================================="
echo "Load Testing Complete!"
echo "==================================="
