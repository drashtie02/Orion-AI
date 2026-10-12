# OrionAI Architecture

## System Overview

OrionAI is a modular RAG system with five core subsystems:

1. **Retrieval Layer**: Hybrid search combining vector similarity and BM25
2. **Agent Layer**: Orchestrated workflow with specialized agents
3. **Evaluation Layer**: Real-time quality assessment
4. **Routing Layer**: Intelligent model selection and cost optimization
5. **Observability Layer**: Metrics, tracing, and monitoring

---

## Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         API Layer                            │
│                    (FastAPI Routes)                          │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      Orchestrator                            │
│  (Coordinates agent execution and manages retry logic)      │
└─┬───────────┬──────────┬──────────┬──────────┬─────────────┘
  │           │          │          │          │
  ▼           ▼          ▼          ▼          ▼
┌────┐    ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
│Plan│    │Retrieve│ │Reason  │ │Evaluate│ │Critic  │
│ner │───▶│  Agent │─▶│ Agent  │─▶│  Layer │─▶│ Agent  │
└────┘    └────────┘ └────────┘ └────────┘ └────────┘
             │           │           │
             ▼           ▼           ▼
        ┌────────┐  ┌────────┐  ┌────────┐
        │Hybrid  │  │Model   │  │Metrics │
        │Retriev │  │Router  │  │Tracker │
        └────────┘  └────────┘  └────────┘
```

---

## Execution Flow

### Query Processing

```
User Query → Planner Agent
    ├─ Classifies task type (factual/analytical/multi-hop/summary)
    ├─ Determines reasoning depth (1-3)
    └─ Decides if retrieval needed
```

### Retrieval Phase

```
Retriever Agent
    ├─ Vector Search (FAISS) - Semantic similarity
    ├─ BM25 Search - Keyword-based ranking
    └─ Hybrid Fusion: Score = α × vector + (1-α) × BM25
```

### Reasoning Phase

```
Reasoner Agent
    ├─ Model Selection (via Model Router)
    ├─ Context Building (fit chunks within token limit)
    └─ LLM Generation (standard or strict mode)
```

### Evaluation Phase

```
Evaluator
    ├─ Faithfulness (sentence-level similarity to context)
    ├─ Relevance (query-context alignment)
    ├─ Hallucination Detection (number/date/noun mismatch)
    ├─ Source Coverage (word overlap ratio)
    └─ Confidence Score (weighted combination)
```

### Critique & Retry

```
Critic Agent
    ├─ Check confidence < threshold
    ├─ If low: Escalate to stronger model or retry with strict mode
    └─ Max 1 retry
```

---

## Device Management

```
DeviceManager
    ├─ Detect CUDA availability
    ├─ Validate compute capability (≥ 12.0 for RTX 5050)
    ├─ Enable GPU optimizations (TF32, cuDNN, FP16)
    └─ Fallback to CPU if needed
```

---

## Model Routing Logic

```
Query → Task Analysis → Model Selection
    ├─ Simple task + low tokens → Cheap model
    ├─ Complex task OR high tokens → Strong model
    └─ Budget exceeded → Force cheap model
    ↓
Generation → Evaluation → Escalation Decision
    ├─ Confidence < threshold → Escalate to strong model
    └─ Confidence OK → Return result
```

---

## Key Design Decisions

1. **Modular Architecture**: Independent, testable components
2. **Device Abstraction**: Centralized hardware management
3. **Deterministic Execution**: Reproducible results
4. **Cost-First Design**: Budget enforcement at runtime
5. **Evaluation-Driven**: Every response evaluated with automatic retry
