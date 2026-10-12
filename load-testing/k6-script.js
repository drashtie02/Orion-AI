import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

const errorRate = new Rate('errors');
const queryLatency = new Trend('query_latency');

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8011';
const API_KEY = __ENV.API_KEY || '';

export const options = {
  stages: [
    { duration: '2m', target: 10 },
    { duration: '5m', target: 50 },
    { duration: '3m', target: 100 },
    { duration: '5m', target: 100 },
    { duration: '2m', target: 50 },
    { duration: '2m', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p(95)<2000', 'p(99)<5000'],
    errors: ['rate<0.05'],
    http_req_failed: ['rate<0.05'],
  },
};

const queries = [
  'What is machine learning?',
  'Explain neural networks',
  'How does deep learning work?',
  'What are transformers in AI?',
  'Describe reinforcement learning',
  'What is natural language processing?',
  'Explain computer vision',
  'How do convolutional neural networks work?',
  'What is transfer learning?',
  'Describe gradient descent optimization',
];

export default function () {
  const query = queries[Math.floor(Math.random() * queries.length)];
  
  const payload = JSON.stringify({
    query: query,
    top_k: 5,
  });

  const params = {
    headers: {
      'Content-Type': 'application/json',
    },
    timeout: '60s',
  };

  if (API_KEY) {
    params.headers['X-API-Key'] = API_KEY;
  }

  const startTime = Date.now();
  const response = http.post(`${BASE_URL}/api/v1/query`, payload, params);
  const duration = Date.now() - startTime;

  queryLatency.add(duration);

  const success = check(response, {
    'status is 200': (r) => r.status === 200,
    'response has answer': (r) => {
      try {
        const body = JSON.parse(r.body);
        return body.answer !== undefined;
      } catch (e) {
        return false;
      }
    },
    'response time < 5s': (r) => r.timings.duration < 5000,
  });

  if (!success) {
    errorRate.add(1);
  } else {
    errorRate.add(0);
  }

  sleep(Math.random() * 2 + 1);
}

export function handleSummary(data) {
  return {
    'stdout': textSummary(data, { indent: ' ', enableColors: true }),
    'load-testing/results.json': JSON.stringify(data, null, 2),
  };
}

function textSummary(data, options) {
  const indent = options.indent || '';
  const enableColors = options.enableColors || false;

  let summary = '\n';
  summary += `${indent}Test Summary:\n`;
  summary += `${indent}  Duration: ${data.state.testRunDurationMs / 1000}s\n`;
  summary += `${indent}  Iterations: ${data.metrics.iterations.values.count}\n`;
  summary += `${indent}  VUs: ${data.metrics.vus.values.value}\n\n`;

  summary += `${indent}HTTP Metrics:\n`;
  summary += `${indent}  Requests: ${data.metrics.http_reqs.values.count}\n`;
  summary += `${indent}  Request Rate: ${data.metrics.http_reqs.values.rate.toFixed(2)}/s\n`;
  summary += `${indent}  Failed Requests: ${(data.metrics.http_req_failed.values.rate * 100).toFixed(2)}%\n\n`;

  summary += `${indent}Latency:\n`;
  summary += `${indent}  Avg: ${data.metrics.http_req_duration.values.avg.toFixed(2)}ms\n`;
  summary += `${indent}  Min: ${data.metrics.http_req_duration.values.min.toFixed(2)}ms\n`;
  summary += `${indent}  Max: ${data.metrics.http_req_duration.values.max.toFixed(2)}ms\n`;
  summary += `${indent}  p50: ${data.metrics.http_req_duration.values['p(50)'].toFixed(2)}ms\n`;
  summary += `${indent}  p90: ${data.metrics.http_req_duration.values['p(90)'].toFixed(2)}ms\n`;
  summary += `${indent}  p95: ${data.metrics.http_req_duration.values['p(95)'].toFixed(2)}ms\n`;
  summary += `${indent}  p99: ${data.metrics.http_req_duration.values['p(99)'].toFixed(2)}ms\n\n`;

  if (data.metrics.errors) {
    summary += `${indent}Error Rate: ${(data.metrics.errors.values.rate * 100).toFixed(2)}%\n`;
  }

  return summary;
}
