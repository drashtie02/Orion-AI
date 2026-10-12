from typing import Dict, List
import time
import asyncio
from core.logging import setup_logger

logger = setup_logger(__name__)

class OrchestratorAsync:
    def __init__(self, retriever, llm_router, evaluator, critic_threshold=0.6, retry_enabled=True, 
                 model_router=None, budget_limit=None):
        self.retriever = retriever
        self.llm_router = llm_router
        self.evaluator = evaluator
        self.critic_threshold = critic_threshold
        self.retry_enabled = retry_enabled
        self.model_router = model_router
        self.budget_limit = budget_limit
        self.trace = []
    
    def _add_trace(self, step: str, agent: str, latency: float, tokens: Dict, summary: str):
        self.trace.append({
            "step": step,
            "agent": agent,
            "latency": round(latency, 4),
            "tokens": tokens,
            "summary": summary
        })
    
    async def execute(self, query: str, top_k: int = 5) -> Dict:
        self.trace = []
        routing_info = {
            "initial_model": None,
            "final_model": None,
            "escalated": False,
            "estimated_cost": 0.0
        }
        
        try:
            start = time.time()
            retrieved_chunks = await self.retriever.search(query, top_k)
            retrieval_latency = time.time() - start
            
            self._add_trace(
                "retrieval",
                "retriever",
                retrieval_latency,
                {},
                f"Retrieved {len(retrieved_chunks)} chunks"
            )
            
            selected_model = None
            if self.model_router:
                context_text = " ".join([chunk['chunk']['text'] for chunk in retrieved_chunks])
                estimated_tokens = len(context_text.split()) + len(query.split())
                selected_model = self.model_router.cheap_model
                routing_info["initial_model"] = selected_model
            
            context_text = "\\n\\n".join([f"[{i+1}] {chunk['chunk']['text']}" for i, chunk in enumerate(retrieved_chunks)])
            prompt = f"""Answer the question based on the following context:

Context:
{context_text}

Question: {query}

Answer:"""
            
            start = time.time()
            llm_response = await self.llm_router.generate(prompt, model_name=selected_model)
            reason_latency = time.time() - start
            
            answer = llm_response['text']
            token_usage = {
                'input_tokens': llm_response['tokens_input'],
                'output_tokens': llm_response['tokens_output']
            }
            model_used = llm_response.get('model_name', selected_model or 'unknown')
            
            self._add_trace(
                "reasoning",
                "reasoner",
                reason_latency,
                token_usage,
                f"Generated answer ({token_usage.get('output_tokens', 0)} tokens) using {model_used}"
            )
            
            start = time.time()
            context_texts = [chunk['chunk']['text'] for chunk in retrieved_chunks]
            evaluation_result = await self._evaluate_async(query, answer, context_texts)
            eval_latency = time.time() - start
            
            self._add_trace(
                "evaluation",
                "evaluator",
                eval_latency,
                {},
                f"Confidence: {evaluation_result.get('confidence_score', 0):.3f}" if evaluation_result else "Failed"
            )
            
            routing_info["final_model"] = model_used
            
            return {
                "answer": answer,
                "sources": [
                    {
                        "chunk_id": chunk['chunk']['chunk_id'],
                        "source": chunk['chunk']['source_path'],
                        "vector_score": round(chunk['vector_score'], 4),
                        "bm25_score": round(chunk['bm25_score'], 4),
                        "hybrid_score": round(chunk['hybrid_score'], 4)
                    }
                    for chunk in retrieved_chunks
                ],
                "evaluation": evaluation_result,
                "trace": self.trace,
                "routing": routing_info
            }
        
        except Exception as e:
            logger.error(f"Orchestration failed: {str(e)}")
            self._add_trace("error", "orchestrator", 0.0, {}, f"Failed: {str(e)}")
            
            return {
                "answer": "Error processing query",
                "sources": [],
                "evaluation": None,
                "trace": self.trace,
                "routing": routing_info
            }
    
    async def _evaluate_async(self, query: str, answer: str, context_texts: List[str]):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.evaluator.evaluate,
            query,
            answer,
            context_texts
        )
