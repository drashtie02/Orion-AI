from typing import Dict
from .base_agent import BaseAgent

class CriticAgent(BaseAgent):
    def __init__(self, threshold: float = 0.6):
        self.threshold = threshold
    
    def execute(self, input_data: Dict) -> Dict:
        evaluation = input_data.get('evaluation', {})
        
        if not evaluation:
            return {
                "output": {"needs_retry": False},
                "metadata": {"agent": "critic", "reason": "no_evaluation"}
            }
        
        confidence_score = evaluation.get('confidence_score', 1.0)
        
        needs_retry = confidence_score < self.threshold
        reason = f"Confidence {confidence_score:.3f} below threshold {self.threshold}" if needs_retry else "Passed"
        
        return {
            "output": {
                "needs_retry": needs_retry,
                "reason": reason
            },
            "metadata": {
                "agent": "critic",
                "confidence_score": confidence_score,
                "threshold": self.threshold
            }
        }
