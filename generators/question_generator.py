import json
import os
from typing import Optional, List
from anthropic import Anthropic
from dotenv import load_dotenv

from models.question import Question
from prompts.generation_prompt import get_generate_questions_prompt

load_dotenv()


class QuestionGenerator:
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.client = Anthropic(api_key=api_key or os.getenv("ANTHROPIC_API_KEY"))
        self.model = model or "claude-3-7-sonnet-latest"
        
    def generate_questions(self, count: int = 1) -> List[Question]:
        """Generate multiple SAT math questions, handling batching internally for large counts"""
        
        # For small counts, generate all at once
        if count <= 10:
            return self._generate_batch(count)
        
        # For larger counts, generate in chunks of 10
        questions = []
        chunks = (count + 9) // 10  # Round up division
        
        for chunk_idx in range(chunks):
            remaining = count - len(questions)
            chunk_size = min(10, remaining)
            
            try:
                chunk_questions = self._generate_batch(chunk_size)
                questions.extend(chunk_questions)
            except Exception as e:
                # Re-raise with more context
                raise ValueError(f"Failed to generate chunk {chunk_idx + 1} of {chunks}: {e}")
        
        return questions
    
    def _generate_batch(self, count: int) -> List[Question]:
        """Generate a batch of questions in a single API call (max 10)"""
        
        prompt = get_generate_questions_prompt(count)
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4000,  # Increased for multiple questions
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        # Extract JSON from response
        content = response.content[0].text
        
        # Try to parse JSON from the response
        try:
            # For multiple questions, look for JSON array
            start_idx = content.find('[')
            end_idx = content.rfind(']') + 1
            json_str = content[start_idx:end_idx]
            
            questions_data = json.loads(json_str)
            
            # Create and return Question objects
            questions = []
            for q_data in questions_data:
                questions.append(Question(**q_data))
            
            return questions
            
        except (json.JSONDecodeError, ValueError) as e:
            raise ValueError(f"Failed to parse questions from response: {e}\nResponse: {content}")