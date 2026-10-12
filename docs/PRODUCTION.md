# Production Deployment Guide

## Prerequisites

- Docker and Docker Compose installed
- Redis instance (included in docker-compose)
- Environment variables configured

## Environment Configuration

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Required variables:
- `OPENAI_API_KEY` - Your OpenAI API key
- `REDIS_ENABLED` - Enable Redis caching (true/false)
- `RATE_LIMIT_ENABLED` - Enable rate limiting (true/false)
- `LOG_LEVEL` - Logging level (INFO, DEBUG, WARNING, ERROR)
- `ENVIRONMENT` - Environment mode (production/development)

## Deployment Steps

### 1. Build Images

```bash
docker-compose build
```

### 2. Start Services

CPU deployment:
```bash
docker-compose up -d orionai-cpu redis
```

GPU deployment:
```bash
docker-compose up -d orionai-gpu redis
```

### 3. Verify Deployment

Check health:
```bash
curl http://localhost:8011/health
```

Check logs:
```bash
docker-compose logs -f
```

### 4. Run Tests in Container

```bash
docker exec orionai-cpu pytest
```

## Monitoring

All logs are in JSON format for easy parsing by log aggregation tools (ELK, Splunk, etc.).

Key log fields:
- `timestamp` - ISO 8601 timestamp
- `level` - Log level
- `request_id` - Unique request identifier
- `endpoint` - API endpoint
- `latency` - Request latency in seconds
- `model_used` - LLM model used
- `cache_hit` - Whether cache was hit

## Rate Limiting

Default: 100 requests per 60 seconds per IP

Configure via environment variables:
- `RATE_LIMIT_REQUESTS`
- `RATE_LIMIT_WINDOW_SECONDS`

## Caching

Redis caching is enabled by default with 1-hour TTL.

Configure via:
- `CACHE_TTL` - Cache TTL in seconds

## Scaling

To scale horizontally:

```bash
docker-compose up -d --scale orionai-cpu=3
```

Add a load balancer (nginx, traefik) in front of the instances.

## Security

- All containers run as non-root user
- No debug mode in production
- Rate limiting enabled by default
- Request ID tracing for audit trails

## Troubleshooting

### Redis Connection Issues

Check Redis health:
```bash
docker exec orionai-redis redis-cli ping
```

### High Memory Usage

Reduce batch sizes in `config.yaml`:
```yaml
cpu_batch_size: 4
gpu_batch_size: 16
```

### Rate Limit Issues

Disable temporarily:
```bash
RATE_LIMIT_ENABLED=false docker-compose up -d
```
