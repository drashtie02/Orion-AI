# Frequently Asked Questions

## General

**Q: What is OrionAI?**  
A: OrionAI is a production-grade RAG system with hybrid retrieval, intelligent model routing, and real-time evaluation.

**Q: Who should use OrionAI?**  
A: ML engineers, researchers, and teams deploying RAG systems that need cost optimization and quality control.

**Q: Is OrionAI free?**  
A: Yes, OrionAI is open-source under MIT license. LLM API costs apply separately.

## Installation

**Q: What Python version is required?**  
A: Python 3.8 or higher.

**Q: Do I need a GPU?**  
A: No. OrionAI runs on CPU with automatic optimization. GPU is optional for acceleration.

**Q: Which GPUs are supported?**  
A: NVIDIA GPUs with compute capability ≥ 12.0 (RTX 5050, RTX 40/50 series). Older GPUs fall back to CPU.

**Q: How do I install for CPU only?**  
A: `pip install torch --index-url https://download.pytorch.org/whl/cpu && pip install -r requirements-cpu.txt`

## Configuration

**Q: How do I configure model routing?**  
A: Edit `config.yaml` under `models` and `routing_config` sections. Define cheap/strong models and thresholds.

**Q: How do I set a budget limit?**  
A: Set `monthly_budget_limit` in `config.yaml`. System enforces this at runtime.

**Q: Can I use local models?**  
A: Yes. Set `llm_type: local` and specify a HuggingFace model name.

**Q: How do I adjust retrieval strategy?**  
A: Change `retrieval_alpha` in config (0=BM25 only, 1=vector only, 0.5=balanced hybrid).

## Usage

**Q: How do I ingest documents?**  
A: `python scripts/ingest_documents.py <path_to_docs>`

**Q: What document formats are supported?**  
A: Currently `.txt` files. Extend `ingest_documents.py` for other formats.

**Q: How do I query the system?**  
A: Start API with `python main.py`, then POST to `/api/v1/query` with JSON payload.

**Q: Can I disable agent orchestration?**  
A: Yes. Set `use_orchestrator: false` in query request for direct retrieval+LLM.

## Performance

**Q: How do I improve speed?**  
A: Use GPU, enable mixed precision, increase batch sizes, or use smaller embedding models.

**Q: How do I reduce costs?**  
A: Lower `confidence_threshold` to reduce retries, use cheaper models, or adjust `token_threshold`.

**Q: What's the expected latency?**  
A: CPU: 2-5s per query. GPU: 0.5-2s per query. Varies by model and document count.

## Troubleshooting

**Q: GPU not detected?**  
A: Run `python scripts/validate_environment.py` and check CUDA installation with `nvidia-smi`.

**Q: Out of memory errors?**  
A: Reduce `gpu_batch_size` or `cpu_batch_size` in config. Use smaller models.

**Q: Import errors?**  
A: Ensure PyTorch is installed first, then run `pip install -r requirements-*.txt`.

**Q: Low confidence scores?**  
A: Check document quality, adjust chunk size, or use stronger embedding models.

## Development

**Q: How do I add a new model?**  
A: Implement `BaseModel` interface in `llm/`, add to `LLMRouter`, configure in `config.yaml`.

**Q: How do I add a new evaluator?**  
A: Create evaluator class in `evaluation/`, integrate in `Evaluator.evaluate()`.

**Q: How do I run benchmarks?**  
A: `python scripts/run_benchmark.py`. Results saved to `artifacts/benchmark_results.json`.

**Q: How do I contribute?**  
A: See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.
