from typing import Dict
from .base_agent import BaseAgent

class ReasonerAgent(BaseAgent):
    def __init__(self, llm):
        self.llm = llm
    
    def execute(self, input_data: Dict) -> Dict:
        query = input_data['query']
        context_chunks = input_data.get('context_chunks', [])
        strict_mode = input_data.get('strict_mode', False)
        model_name = input_data.get('model_name', None)
        
        context_text = "\n\n".join([f"[{i+1}] {chunk['chunk']['text']}" for i, chunk in enumerate(context_chunks)])
        
        if strict_mode:
            prompt = f"""Answer ONLY using the context below. Do not add information not present in the context.

Context:
{context_text}

Question: {query}

Answer:"""
        else:
            prompt = f"""Answer the question based on the following context:

Context:
{context_text}

Question: {query}

Answer:"""
        
        response = self.llm.generate(prompt, model_name)
        
        return {
            "output": {
                "answer": response.get('text', str(response)) if isinstance(response, dict) else str(response),
                "token_usage": {
                    "input_tokens": response.get('tokens_input', 0) if isinstance(response, dict) else 0,
                    "output_tokens": response.get('tokens_output', 0) if isinstance(response, dict) else 0
                },
                "model_used": response.get('model_name', model_name or 'unknown') if isinstance(response, dict) else model_name or 'unknown'
            },
            "metadata": {"agent": "reasoner", "strict_mode": strict_mode, "model_name": model_name}
        }
