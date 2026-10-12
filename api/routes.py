from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, Dict, List
from retrieval.hybrid_async import HybridRetrieverAsync
from llm.router_async import LLMRouterAsync
from observability.token_tracker import TokenTracker
from observability.latency_tracker import LatencyTracker
from evaluation.evaluator import Evaluator
from core.orchestrator_async import OrchestratorAsync
from core.config import config
from core.cache import cache_manager
from core.logging import setup_logger
from pathlib import Path
import json
import asyncio

logger = setup_logger(__name__)
router = APIRouter()

class QueryRequest(BaseModel):
    query: str
    top_k: Optional[int] = None
    use_orchestrator: Optional[bool] = True
    stream: Optional[bool] = False

class ContextBuilder:
    def __init__(self, llm_router: LLMRouterAsync):
        self.llm_router = llm_router
        self.max_tokens = config.max_context_tokens
    
    def build_context(self, chunks_data: List[Dict]) -> Dict:
        selected_chunks = []
        total_tokens = 0
        
        for item in chunks_data:
            chunk = item['chunk']
            chunk_tokens = self.llm_router.count_tokens(chunk['text'])
            
            if total_tokens + chunk_tokens <= self.max_tokens:
                selected_chunks.append({
                    'text': chunk['text'],
                    'source': chunk['source_path'],
                    'chunk_id': chunk['chunk_id'],
                    'vector_score': item['vector_score'],
                    'bm25_score': item['bm25_score'],
                    'hybrid_score': item['hybrid_score']
                })
                total_tokens += chunk_tokens
            else:
                break
        
        return {'chunks': selected_chunks, 'total_tokens': total_tokens}

retriever = None
llm_router = None
context_builder = None
evaluator = None
orchestrator = None

async def initialize_components():
    global retriever, llm_router, context_builder, evaluator, orchestrator
    
    index_path = config.index_path
    if not Path(f"{index_path}/faiss.index").exists():
        raise FileNotFoundError(f"Index not found at {index_path}. Run ingestion first.")
    
    retriever = HybridRetrieverAsync()
    retriever.load(index_path)
    
    model_configs = config.models if config.models else None
    llm_router = LLMRouterAsync(model_configs)
    context_builder = ContextBuilder(llm_router)
    
    evaluator = Evaluator(retriever.embedding_model, config.evaluation_weights)
    
    model_router = None
    if config.models and config.routing_config:
        from core.model_router import ModelRouter
        model_router = ModelRouter(
            llm_router,
            config.routing_config.get('cheap_model', 'cheap_model'),
            config.routing_config.get('strong_model', 'strong_model'),
            config.routing_config.get('token_threshold', 500),
            config.routing_config.get('confidence_threshold', 0.6)
        )
    
    orchestrator = OrchestratorAsync(
        retriever, 
        llm_router, 
        evaluator, 
        config.critic_threshold,
        True,
        model_router,
        config.monthly_budget_limit
    )

@router.post("/query")
async def query(request_body: QueryRequest, request: Request):
    try:
        if retriever is None:
            await initialize_components()
    except Exception as e:
        logger.error(f"Initialization failed: {str(e)}", extra={'error_type': 'init_error'})
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail="Service initialization failed")
    
    if request_body.stream:
        return StreamingResponse(
            stream_query_response(request_body, request),
            media_type="text/event-stream"
        )
    
    top_k = request_body.top_k or config.top_k_default
    use_orchestrator = request_body.use_orchestrator
    
    cache_key = json.dumps({
        'query': request_body.query,
        'top_k': top_k,
        'use_orchestrator': use_orchestrator
    }, sort_keys=True)
    
    cached_response = await cache_manager.get('query', cache_key)
    if cached_response:
        cached_response['request_id'] = request.state.request_id
        logger.info("Cache hit", extra={'cache_hit': True})
        return cached_response
    
    if use_orchestrator:
        token_tracker = TokenTracker()
        latency_tracker = LatencyTracker()
        
        try:
            with latency_tracker.track('total'):
                result = await orchestrator.execute(request_body.query, top_k)
        except Exception as e:
            logger.error(f"Orchestrator execution failed: {str(e)}", extra={'error_type': 'orchestrator_error'})
            from fastapi import HTTPException
            raise HTTPException(status_code=500, detail=str(e))
        
        total_input_tokens = sum(step['tokens'].get('input_tokens', 0) for step in result['trace'])
        total_output_tokens = sum(step['tokens'].get('output_tokens', 0) for step in result['trace'])
        
        if total_input_tokens > 0 or total_output_tokens > 0:
            token_tracker.track(total_input_tokens, total_output_tokens, llm_router.model_name)
        
        response = {
            'answer': result['answer'],
            'sources': result['sources'],
            'metrics': {
                'latency': latency_tracker.get_metrics(),
                'tokens': token_tracker.get_metrics() if total_input_tokens > 0 else {}
            },
            'evaluation': result['evaluation'],
            'trace': result['trace'],
            'routing': result.get('routing', {}),
            'request_id': request.state.request_id
        }
    
    else:
        token_tracker = TokenTracker()
        latency_tracker = LatencyTracker()
        
        with latency_tracker.track('retrieval'):
            results = await retriever.search(request_body.query, top_k)
        
        context_data = context_builder.build_context(results)
        context_text = "\n\n".join([f"[{i+1}] {chunk['text']}" for i, chunk in enumerate(context_data['chunks'])])
        
        prompt = f"""Answer the question based on the following context:

Context:
{context_text}

Question: {request_body.query}

Answer:"""
        
        with latency_tracker.track('llm'):
            llm_response = await llm_router.generate(prompt)
        
        token_tracker.track(
            llm_response['tokens_input'],
            llm_response['tokens_output'],
            llm_response['model_name']
        )
        
        evaluation_result = None
        try:
            context_texts = [chunk['text'] for chunk in context_data['chunks']]
            loop = asyncio.get_event_loop()
            evaluation_result = await loop.run_in_executor(
                None,
                evaluator.evaluate,
                request_body.query,
                llm_response['text'],
                context_texts
            )
        except Exception as e:
            logger.error(f"Evaluation failed: {str(e)}", extra={'error_type': 'evaluation_error'})
        
        response = {
            'answer': llm_response['text'],
            'sources': [
                {
                    'chunk_id': chunk['chunk_id'],
                    'source': chunk['source'],
                    'vector_score': round(chunk['vector_score'], 4),
                    'bm25_score': round(chunk['bm25_score'], 4),
                    'hybrid_score': round(chunk['hybrid_score'], 4)
                }
                for chunk in context_data['chunks']
            ],
            'metrics': {
                'latency': latency_tracker.get_metrics(),
                'tokens': token_tracker.get_metrics()
            },
            'evaluation': evaluation_result,
            'request_id': request.state.request_id
        }
    
    await cache_manager.set('query', cache_key, response)
    logger.info("Cache miss", extra={'cache_hit': False})
    
    return response

async def stream_query_response(request_body: QueryRequest, request: Request):
    try:
        if retriever is None:
            await initialize_components()
        
        request_id = request.state.request_id
        top_k = request_body.top_k or config.top_k_default
        
        yield f"data: {{\"type\": \"start\", \"request_id\": \"{request_id}\"}}\n\n"
        
        results = await retriever.search(request_body.query, top_k)
        
        context_data = context_builder.build_context(results)
        context_text = "\n\n".join([f"[{i+1}] {chunk['text']}" for i, chunk in enumerate(context_data['chunks'])])
        
        prompt = f"""Answer the question based on the following context:

Context:
{context_text}

Question: {request_body.query}

Answer:"""
        
        async for chunk in llm_router.generate_stream(prompt):
            yield f"data: {{\"type\": \"token\", \"content\": {json.dumps(chunk)}}}\n\n"
        
        sources = [
            {
                'chunk_id': chunk['chunk_id'],
                'source': chunk['source'],
                'hybrid_score': round(chunk['hybrid_score'], 4)
            }
            for chunk in context_data['chunks']
        ]
        
        yield f"data: {{\"type\": \"sources\", \"sources\": {json.dumps(sources)}}}\n\n"
        yield f"data: {{\"type\": \"end\", \"request_id\": \"{request_id}\"}}\n\n"
    
    except asyncio.CancelledError:
        logger.info("Stream cancelled by client", extra={'request_id': request.state.request_id})
        raise
    except Exception as e:
        logger.error(f"Stream error: {str(e)}", extra={'request_id': request.state.request_id})
        yield f"data: {{\"type\": \"error\", \"error\": {json.dumps(str(e))}}}\n\n"
