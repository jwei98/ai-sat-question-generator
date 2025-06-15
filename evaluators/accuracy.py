import json
import os
from typing import Dict, Optional
from anthropic import Anthropic
from dotenv import load_dotenv

from models.question import Question
from prompts.evaluation_prompts import get_accuracy_prompt

load_dotenv()


class AccuracyEvaluator:
    def __init__(self, api_key: Optional[str] = None):
        self.client = Anthropic(api_key=api_key or os.getenv("ANTHROPIC_API_KEY"))
    
    def evaluate(self, question: Question) -> Dict[str, any]:
        """Evaluate the mathematical accuracy of a question"""
        
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2000,
            messages=[
                {"role": "user", "content": get_accuracy_prompt(question)}
            ]
        )
        
        content = response.content[0].text
        
        try:
            # Find JSON in the response
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            
            if start_idx == -1 or end_idx == 0:
                # Try to extract boolean value from response
                correct = "correct" in content.lower() and "true" in content.lower()
                return {
                    "correct": correct,
                    "explanation": "Extracted from response",
                    "solution_steps": content
                }
            
            json_str = content[start_idx:end_idx]
            
            # Clean up the JSON string - remove any line breaks within string values
            import re
            json_str = re.sub(r'"\s*:\s*"[^"]*\n[^"]*"', lambda m: m.group(0).replace('\n', ' '), json_str)
            
            result = json.loads(json_str)
            
            return {
                "correct": result.get("correct", False),
                "explanation": result.get("explanation", ""),
                "solution_steps": result.get("solution_steps", "")
            }
            
        except (json.JSONDecodeError, ValueError) as e:
            # If we can't parse JSON, return a default response
            return {
                "correct": False,
                "explanation": f"Failed to parse evaluation response: {e}",
                "solution_steps": content
            }