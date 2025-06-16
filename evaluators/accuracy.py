from typing import Dict, Optional

from models.question import Question
from prompts.evaluation_prompts import get_accuracy_prompt
from .base import BaseEvaluator


class AccuracyEvaluator(BaseEvaluator):
    
    def evaluate(self, question: Question) -> Dict[str, any]:
        """Evaluate the mathematical accuracy of a question"""
        
        prompt = get_accuracy_prompt(question)
        content = self.call_api(prompt)
        
        try:
            result = self.parse_json_response(content)
            
            return {
                "correct": result.get("correct", False),
                "explanation": result.get("explanation", ""),
                "solution_steps": result.get("solution_steps", "")
            }
            
        except ValueError:
            # If we can't parse JSON, try to extract boolean value from response
            correct = "correct" in content.lower() and "true" in content.lower()
            return {
                "correct": correct,
                "explanation": "Extracted from response",
                "solution_steps": content
            }