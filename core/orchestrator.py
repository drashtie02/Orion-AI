from typing import Dict, List
import time
from agents.planner import PlannerAgent
from agents.retriever_agent import RetrieverAgent
from agents.reasoner_agent import ReasonerAgent
from agents.critic_agent import CriticAgent
from evaluation.evaluator import Evaluator
from core.model_router import ModelRouter
from observability.token_tracker import TokenTracker
from core.logging import setup_logger

logger = setup_logger(__name__)

class Orchestrator:
    def __init__(self, retriever, llm_router, evaluator, critic_threshold=0.6, retry_enabled=True, 
                 model_router=None, budget_limit=None):
        self.planner = PlannerAgent(llm_router)
        self.retriever_agent = RetrieverAgent(retriever)
        self.reasoner = ReasonerAgent(llm_router)
        self.critic = CriticAgent(threshold=critic_threshold)
        self.evaluator = evaluator
        self.retry_enabled = retry_enabled
        self.model_router = model_router
        self.budget_limit = budget_limit
        self.token_tracker = TokenTracker()
        self.trace = []
    
    def _add_trace(self, step: str, agent: str, latency: float, tokens: Dict, summary: str):
        self.trace.append({
            "step": step,
            "agent": agent,
            "latency": round(latency, 4),
            "tokens": tokens,
            "summary": summary
        })
    
    def execute(self, query: str, top_k: int = 5) -> Dict:
        self.trace = []
        routing_info = {
            "initial_model": None,
            "final_model": None,
            "escalated": False,
            "estimated_cost": 0.0
        }
        
        budget_exceeded = self.budget_limit and self.token_tracker.get_cumulative_cost() >= self.budget_limit
        if budget_exceeded:
            logger.warning(f"Budget exceeded: {self.token_tracker.get_cumulative_cost():.2f}/{self.budget_limit}")
        
        try:
            start = time.time()
            plan_result = self.planner.execute({"query": query})
            plan_latency = time.time() - start
            
            plan_output = plan_result['output']
            self._add_trace(
                "planning",
                "planner",
                plan_latency,
                {},
                f"Task: {plan_output['task_type']}, Depth: {plan_output['reasoning_depth']}"
            )
            
            retrieval_required = plan_output.get('retrieval_required', True)
            
            if retrieval_required:
                start = time.time()
                retrieval_result = self.retriever_agent.execute({"query": query, "top_k": top_k})
                retrieval_latency = time.time() - start
                
                retrieved_chunks = retrieval_result['output']['retrieved_chunks']
                self._add_trace(
                    "retrieval",
                    "retriever",
                    retrieval_latency,
                    {},
                    f"Retrieved {len(retrieved_chunks)} chunks"
                )
            else:
                retrieved_chunks = []
                self._add_trace("retrieval", "retriever", 0.0, {}, "Skipped")
            
            selected_model = None
            if self.model_router and not budget_exceeded:
                context_text = " ".join([chunk['chunk']['text'] for chunk in retrieved_chunks])
                estimated_tokens = len(context_text.split()) + len(query.split())
                selected_model = self.model_router.select_initial_model(
                    plan_output['task_type'],
                    plan_output['reasoning_depth'],
                    estimated_tokens
                )
                routing_info["initial_model"] = selected_model
            elif budget_exceeded and self.model_router:
                selected_model = self.model_router.cheap_model
                routing_info["initial_model"] = selected_model
            
            start = time.time()
            reason_result = self.reasoner.execute({
                "query": query,
                "context_chunks": retrieved_chunks,
                "strict_mode": False,
                "model_name": selected_model
            })
            reason_latency = time.time() - start
            
            answer = reason_result['output']['answer']
            token_usage = reason_result['output']['token_usage']
            model_used = reason_result['output'].get('model_used', selected_model or 'unknown')
            
            if self.model_router:
                self.model_router.record_latency(model_used, reason_latency)
                model_obj = self.reasoner.llm.get_model(model_used)
                if model_obj:
                    cost_info = model_obj.get_cost_info()
                    self.token_tracker.track(
                        token_usage['input_tokens'],
                        token_usage['output_tokens'],
                        model_used,
                        cost_info['cost_per_1k_input'],
                        cost_info['cost_per_1k_output']
                    )
            
            self._add_trace(
                "reasoning",
                "reasoner",
                reason_latency,
                token_usage,
                f"Generated answer ({token_usage.get('output_tokens', 0)} tokens) using {model_used}"
            )
            
            start = time.time()
            context_texts = [chunk['chunk']['text'] for chunk in retrieved_chunks]
            evaluation_result = self.evaluator.evaluate(query, answer, context_texts)
            eval_latency = time.time() - start
            
            self._add_trace(
                "evaluation",
                "evaluator",
                eval_latency,
                {},
                f"Confidence: {evaluation_result.get('confidence_score', 0):.3f}" if evaluation_result else "Failed"
            )
            
            start = time.time()
            critic_result = self.critic.execute({"evaluation": evaluation_result})
            critic_latency = time.time() - start
            
            needs_retry = critic_result['output']['needs_retry'] and self.retry_enabled
            self._add_trace(
                "critique",
                "critic",
                critic_latency,
                {},
                critic_result['output']['reason']
            )
            
            should_escalate = False
            if needs_retry and self.model_router and not budget_exceeded:
                confidence_score = evaluation_result.get('confidence_score', 1.0) if evaluation_result else 1.0
                should_escalate = self.model_router.should_escalate(confidence_score, model_used)
            
            if should_escalate:
                routing_info["escalated"] = True
                
                start = time.time()
                retry_result = self.reasoner.execute({
                    "query": query,
                    "context_chunks": retrieved_chunks,
                    "strict_mode": True,
                    "model_name": self.model_router.strong_model
                })
                retry_latency = time.time() - start
                
                answer = retry_result['output']['answer']
                token_usage = retry_result['output']['token_usage']
                model_used = retry_result['output'].get('model_used', self.model_router.strong_model)
                
                if self.model_router:
                    self.model_router.record_latency(model_used, retry_latency)
                    model_obj = self.reasoner.llm.get_model(model_used)
                    if model_obj:
                        cost_info = model_obj.get_cost_info()
                        self.token_tracker.track(
                            token_usage['input_tokens'],
                            token_usage['output_tokens'],
                            model_used,
                            cost_info['cost_per_1k_input'],
                            cost_info['cost_per_1k_output']
                        )
                
                self._add_trace(
                    "escalation",
                    "reasoner",
                    retry_latency,
                    token_usage,
                    f"Escalated to {model_used}"
                )
                
                start = time.time()
                evaluation_result = self.evaluator.evaluate(query, answer, context_texts)
                eval_latency = time.time() - start
                
                self._add_trace(
                    "retry_evaluation",
                    "evaluator",
                    eval_latency,
                    {},
                    f"Escalation confidence: {evaluation_result.get('confidence_score', 0):.3f}" if evaluation_result else "Failed"
                )
            elif needs_retry:
                start = time.time()
                retry_result = self.reasoner.execute({
                    "query": query,
                    "context_chunks": retrieved_chunks,
                    "strict_mode": True,
                    "model_name": selected_model
                })
                retry_latency = time.time() - start
                
                answer = retry_result['output']['answer']
                token_usage = retry_result['output']['token_usage']
                model_used = retry_result['output'].get('model_used', selected_model or 'unknown')
                
                if self.model_router:
                    model_obj = self.reasoner.llm.get_model(model_used)
                    if model_obj:
                        cost_info = model_obj.get_cost_info()
                        self.token_tracker.track(
                            token_usage['input_tokens'],
                            token_usage['output_tokens'],
                            model_used,
                            cost_info['cost_per_1k_input'],
                            cost_info['cost_per_1k_output']
                        )
                
                self._add_trace(
                    "retry_reasoning",
                    "reasoner",
                    retry_latency,
                    token_usage,
                    "Strict mode retry"
                )
                
                start = time.time()
                evaluation_result = self.evaluator.evaluate(query, answer, context_texts)
                eval_latency = time.time() - start
                
                self._add_trace(
                    "retry_evaluation",
                    "evaluator",
                    eval_latency,
                    {},
                    f"Retry confidence: {evaluation_result.get('confidence_score', 0):.3f}" if evaluation_result else "Failed"
                )
            
            routing_info["final_model"] = model_used
            routing_info["estimated_cost"] = self.token_tracker.get_metrics().get('estimated_cost', 0.0)
            
            if self.model_router:
                self.token_tracker.save_cumulative_cost()
            
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
