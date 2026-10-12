#!/bin/bash

# OrionAI Demo Commands
# Copy-paste ready commands for demo recording

set -e

BASE_URL="${BASE_URL:-http://localhost:8011}"

echo "==================================="
echo "OrionAI Demo Commands"
echo "==================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 1. Health Check
echo -e "${BLUE}[1] Health Check${NC}"
curl -s $BASE_URL/health | jq
echo ""
sleep 2

# 2. Streaming Query
echo -e "${BLUE}[2] Streaming Query (Real-time tokens)${NC}"
curl -X POST $BASE_URL/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is machine learning?",
    "stream": true
  }'
echo ""
sleep 2

# 3. Non-streaming Query
echo -e "${BLUE}[3] Standard Query (Buffered response)${NC}"
curl -X POST $BASE_URL/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Explain neural networks in simple terms",
    "top_k": 5
  }' | jq
echo ""
sleep 2

# 4. Cache Hit Demo
echo -e "${BLUE}[4] Cache Hit (Same query, instant response)${NC}"
echo "First request (cache miss):"
time curl -s -X POST $BASE_URL/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is deep learning?",
    "top_k": 3
  }' | jq -r '.answer' | head -n 3
echo ""

echo "Second request (cache hit):"
time curl -s -X POST $BASE_URL/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is deep learning?",
    "top_k": 3
  }' | jq -r '.answer' | head -n 3
echo ""
sleep 2

# 5. Rate Limiting Demo
echo -e "${BLUE}[5] Rate Limiting (Rapid requests)${NC}"
echo "Sending 10 rapid requests..."
for i in {1..10}; do
  response=$(curl -s -w "\n%{http_code}" -X POST $BASE_URL/api/v1/query \
    -H "Content-Type: application/json" \
    -d "{\"query\": \"Test query $i\"}")
  
  http_code=$(echo "$response" | tail -n 1)
  
  if [ "$http_code" = "429" ]; then
    echo -e "${GREEN}Request $i: Rate limited (429)${NC}"
  else
    echo "Request $i: Success ($http_code)"
  fi
done
echo ""
sleep 2

# 6. Metrics Endpoint
echo -e "${BLUE}[6] Metrics (Observability)${NC}"
curl -s $BASE_URL/metrics | jq
echo ""
sleep 2

# 7. Different Query Types
echo -e "${BLUE}[7] Complex Query (Model routing)${NC}"
curl -X POST $BASE_URL/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Compare supervised learning, unsupervised learning, and reinforcement learning. Provide examples of each.",
    "top_k": 10
  }' | jq '.routing'
echo ""
sleep 2

# 8. Source Attribution
echo -e "${BLUE}[8] Source Attribution (Hybrid retrieval)${NC}"
curl -X POST $BASE_URL/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is transfer learning?",
    "top_k": 5
  }' | jq '.sources'
echo ""

echo -e "${GREEN}==================================="
echo "Demo Complete!"
echo "===================================${NC}"
