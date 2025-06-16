import json
import os
import random
from typing import List, Dict, Tuple, Optional
from anthropic import Anthropic
from dotenv import load_dotenv

from models.question import Question
from prompts.evaluation_prompts import get_authenticity_prompt

load_dotenv()


class AuthenticityEvaluator:
    def __init__(self, api_key: Optional[str] = None):
        self.client = Anthropic(api_key=api_key or os.getenv("ANTHROPIC_API_KEY"))
    
    def evaluate(self, real_questions: List[Dict], generated_questions: List[Question]) -> Dict:
        """
        Evaluate authenticity by mixing real and generated questions and having AI guess which are which.
        
        Returns:
            Dict with:
                - accuracy: float (0-1), lower is better (harder to distinguish)
                - predictions: List of (question_id, is_real, predicted_real)
                - summary: Dict with counts
        """
        
        # Prepare mixed questions with labels
        mixed_questions = []
        
        # Add real questions
        for i, q in enumerate(real_questions):
            mixed_questions.append({
                "id": f"real_{i}",
                "question": q["question"],
                "choices": q["choices"],
                "answer": q["answer"],
                "is_real": True
            })
        
        # Add generated questions
        for i, q in enumerate(generated_questions):
            mixed_questions.append({
                "id": f"gen_{i}",
                "question": q.question,
                "choices": q.choices,
                "answer": q.answer,
                "is_real": False
            })
        
        # Shuffle to randomize order
        random.shuffle(mixed_questions)
        
        # Evaluate each question
        predictions = []
        correct_predictions = 0
        
        for q in mixed_questions:
            # Get AI's prediction
            prompt = get_authenticity_prompt(q)
            
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Extract prediction
            content = response.content[0].text.lower()
            
            # Look for JSON response first
            try:
                start_idx = content.find('{')
                end_idx = content.rfind('}') + 1
                if start_idx != -1 and end_idx != 0:
                    json_str = content[start_idx:end_idx]
                    result = json.loads(json_str)
                    predicted_real = result.get("is_real", "real" in content)
                else:
                    predicted_real = "real" in content and "generated" not in content
            except:
                # Fallback to simple text analysis
                predicted_real = "real" in content and "generated" not in content
            
            predictions.append({
                "id": q["id"],
                "is_real": q["is_real"],
                "predicted_real": predicted_real,
                "correct": q["is_real"] == predicted_real
            })
            
            if q["is_real"] == predicted_real:
                correct_predictions += 1
        
        # Calculate statistics
        total = len(predictions)
        accuracy = correct_predictions / total if total > 0 else 0
        
        real_count = sum(1 for p in predictions if p["is_real"])
        generated_count = total - real_count
        
        real_correct = sum(1 for p in predictions if p["is_real"] and p["correct"])
        generated_correct = sum(1 for p in predictions if not p["is_real"] and p["correct"])
        
        return {
            "accuracy": accuracy,
            "predictions": predictions,
            "summary": {
                "total_questions": total,
                "correct_predictions": correct_predictions,
                "accuracy_percentage": accuracy * 100,
                "real_questions": {
                    "count": real_count,
                    "correctly_identified": real_correct,
                    "accuracy": real_correct / real_count if real_count > 0 else 0
                },
                "generated_questions": {
                    "count": generated_count,
                    "correctly_identified": generated_correct,
                    "accuracy": generated_correct / generated_count if generated_count > 0 else 0
                }
            }
        }