from typing import Dict
from .base_agent import BaseAgent

class PlannerAgent(BaseAgent):
    def __init__(self, llm):
        self.llm = llm
    
    def execute(self, input_data: Dict) -> Dict:
        query = input_data['query']
        
        prompt = f"""Classify this query and respond ONLY with valid JSON:

Query: {query}

Respond with:
{{
  "task_type": "factual" or "analytical" or "multi-hop" or "summary",
  "reasoning_depth": 1-3,
  "retrieval_required": true or false
}}

JSON:"""
        
        response = self.llm.generate(prompt)
        text = response.get('text', '') if isinstance(response, dict) else str(response)
        
        task_type = "factual"
        reasoning_depth = 1
        retrieval_required = True
        
        if "analytical" in text.lower():
            task_type = "analytical"
            reasoning_depth = 2
        elif "multi-hop" in text.lower() or "multi hop" in text.lower():
            task_type = "multi-hop"
            reasoning_depth = 3
        elif "summary" in text.lower():
            task_type = "summary"
            reasoning_depth = 2
        
        if "retrieval_required" in text.lower() and "false" in text.lower():
            retrieval_required = False
        
        return {
            "output": {
                "task_type": task_type,
                "reasoning_depth": reasoning_depth,
                "retrieval_required": retrieval_required
            },
            "metadata": {"agent": "planner"}
        }