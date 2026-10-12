import re
from typing import List, Dict

class HallucinationDetector:
    def _extract_numbers(self, text: str) -> set:
        return set(re.findall(r'\b\d+(?:\.\d+)?\b', text))
    
    def _extract_dates(self, text: str) -> set:
        dates = set()
        dates.update(re.findall(r'\b\d{4}\b', text))
        dates.update(re.findall(r'\b\d{1,2}/\d{1,2}/\d{2,4}\b', text))
        dates.update(re.findall(r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}\b', text, re.IGNORECASE))
        return dates
    
    def _extract_proper_nouns(self, text: str) -> set:
        words = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        return set(words)
    
    def _is_present(self, item: str, context: str) -> bool:
        return item.lower() in context.lower()
    
    def evaluate(self, answer: str, context_chunks: List[str]) -> Dict:
        context_text = " ".join(context_chunks)
        flags = []
        risk_score = 0.0
        
        answer_numbers = self._extract_numbers(answer)
        context_numbers = self._extract_numbers(context_text)
        missing_numbers = answer_numbers - context_numbers
        if missing_numbers:
            flags.append(f"Numbers not in context: {list(missing_numbers)}")
            risk_score += 0.3
        
        answer_dates = self._extract_dates(answer)
        context_dates = self._extract_dates(context_text)
        missing_dates = answer_dates - context_dates
        if missing_dates:
            flags.append(f"Dates not in context: {list(missing_dates)}")
            risk_score += 0.3
        
        answer_nouns = self._extract_proper_nouns(answer)
        missing_nouns = [noun for noun in answer_nouns if not self._is_present(noun, context_text)]
        if missing_nouns:
            flags.append(f"Proper nouns not in context: {missing_nouns}")
            risk_score += 0.2
        
        hallucination_risk = min(risk_score, 1.0)
        
        return {
            "hallucination_risk": hallucination_risk,
            "flags": flags
        }
