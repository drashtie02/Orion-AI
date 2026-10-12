#!/bin/bash
set -e

echo "Building Docker images..."
docker-compose build

echo "Starting services..."
docker-compose up -d

echo "Waiting for services to be healthy..."
sleep 10

echo "Running health check..."
curl -f http://localhost:8011/health || exit 1

echo "Testing query endpoint..."
curl -X POST http://localhost:8011/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"query": "test", "top_k": 5}' || exit 1

echo "Running tests inside container..."
docker exec orionai-cpu pytest --cov=. --cov-report=term || exit 1

echo "Checking logs for errors..."
docker-compose logs | grep -i error && exit 1 || echo "No errors found"

echo "Stopping services..."
docker-compose down

echo "All tests passed!"
