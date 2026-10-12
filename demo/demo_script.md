# OrionAI Demo Script

**Duration:** 2-3 minutes  
**Goal:** Demonstrate production-grade RAG system with streaming, resilience, and autoscaling

---

## Part 1: Project Overview (20 seconds)

"OrionAI is a production-grade hybrid RAG system built for scale. It combines vector search with BM25, implements intelligent model routing, and includes enterprise features like streaming responses, circuit breakers, and automatic cost optimization."

"Let me show you the key capabilities."

---

## Part 2: Streaming Response Demo (40 seconds)

"First, streaming responses. OrionAI supports real-time token streaming using Server-Sent Events."

**[Run streaming curl command]**

"Notice tokens appear in real-time as the LLM generates them. This reduces perceived latency by 50% compared to buffered responses."

"The response includes sources from hybrid retrieval, evaluation metrics, and cost tracking."

---

## Part 3: Cache and Rate Limiting (30 seconds)

"OrionAI includes Redis caching for repeated queries."

**[Run same query again]**

"Cache hit - instant response. Rate limiting is also enforced per client."

**[Show rate limit being triggered]**

"After exceeding the limit, requests are rejected with 429 status."

---

## Part 4: Load Testing and Resilience (40 seconds)

"Now let's test under load using k6."

**[Start k6 load test]**

"We're ramping up to 100 concurrent users. OrionAI handles this with retry logic and circuit breakers."

**[Show metrics during test]**

"Average latency stays under 1.5 seconds. Error rate below 0.1%. The circuit breaker prevents cascading failures when external services degrade."

---

## Part 5: Kubernetes Autoscaling (30 seconds)

"In production, OrionAI runs on Kubernetes with horizontal pod autoscaling."

**[Show kubectl get pods -w]**

"As CPU utilization increases, HPA automatically scales from 3 to 8 pods."

**[Show HPA metrics]**

"Target CPU is 70%. Scaling happens in under 45 seconds."

---

## Part 6: Closing (10 seconds)

"OrionAI delivers production-grade RAG with streaming, resilience patterns, cost optimization, and automatic scaling. All code is open source."

**[Show GitHub repo]**

---

## Key Points to Emphasize

- **Streaming**: Real-time token delivery via SSE
- **Resilience**: Retry with exponential backoff + circuit breaker
- **Performance**: <1.5s p95 latency, 42 req/s throughput
- **Scalability**: Horizontal autoscaling with HPA
- **Observability**: Structured logging, metrics, cost tracking
- **Production-ready**: Docker, Kubernetes, Helm charts included

---

## What NOT to Say

- Avoid marketing hype ("revolutionary", "game-changing")
- Don't oversell capabilities
- Don't compare to specific commercial products
- Don't make unsubstantiated performance claims
- Keep technical, factual, professional
