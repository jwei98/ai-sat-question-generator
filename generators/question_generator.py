import json
import os
from typing import Optional, List
from anthropic import Anthropic
from dotenv import load_dotenv

from models.question import Question
from prompts.generation_prompt import GENERATION_SYSTEM_PROMPT, get_generate_questions_prompt

load_dotenv()


class QuestionGenerator:
    def __init__(self, api_key: Optional[str] = None):
        self.client = Anthropic(api_key=api_key or os.getenv("ANTHROPIC_API_KEY"))
        
    def generate_questions(self, count: int = 1) -> List[Question]:
        """Generate multiple SAT math questions in a single API call"""
        
        prompt = get_generate_questions_prompt(count)
        
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4000,  # Increased for multiple questions
            system=GENERATION_SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        # Extract JSON from response
        content = response.content[0].text
        
        # Try to parse JSON from the response
        try:
            if count == 1:
                # For single question, look for JSON object
                start_idx = content.find('{')
                end_idx = content.rfind('}') + 1
                json_str = content[start_idx:end_idx]
                
                question_data = json.loads(json_str)
                return [Question(**question_data)]
            else:
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