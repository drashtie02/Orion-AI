#!/bin/bash
set -e

echo "🔧 Fixing Docker weight download issue..."
echo ""

echo "1️⃣ Stopping containers..."
docker compose down

echo ""
echo "2️⃣ Removing old image..."
docker rmi orionai:cpu 2>/dev/null || echo "Image not found, skipping..."

echo ""
echo "3️⃣ Rebuilding with model pre-download..."
docker compose build orionai-cpu

echo ""
echo "4️⃣ Starting services..."
docker compose up -d orionai-cpu redis

echo ""
echo "5️⃣ Waiting for startup..."
sleep 10

echo ""
echo "✅ Done! Checking logs..."
echo ""
docker logs orionai-cpu --tail 20

echo ""
echo "🧪 Test with:"
echo "curl -X POST http://localhost:8011/api/v1/query -H 'Content-Type: application/json' -d '{\"query\": \"test\", \"top_k\": 3}'"
