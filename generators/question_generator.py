import json
import os
from typing import Optional
from anthropic import Anthropic
from dotenv import load_dotenv

from models.question import Question
from prompts.generation_prompt import GENERATION_SYSTEM_PROMPT, FEW_SHOT_EXAMPLES

load_dotenv()


class QuestionGenerator:
    def __init__(self, api_key: Optional[str] = None):
        self.client = Anthropic(api_key=api_key or os.getenv("ANTHROPIC_API_KEY"))
        
    def generate_question(self) -> Question:
        """Generate a single SAT math question"""
        
        # Build few-shot examples
        examples_text = "Here are some example SAT questions:\n\n"
        for i, example in enumerate(FEW_SHOT_EXAMPLES, 1):
            examples_text += f"Example {i}:\n"
            examples_text += json.dumps(example, indent=2)
            examples_text += "\n\n"
        
        prompt = f"{examples_text}Now generate a new SAT math question following the same format. Make it unique and different from the examples."
        
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            system=GENERATION_SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        # Extract JSON from response
        content = response.content[0].text
        
        # Try to parse JSON from the response
        try:
            # Find JSON in the response
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            json_str = content[start_idx:end_idx]
            
            question_data = json.loads(json_str)
            
            # Create and return Question object
            return Question(**question_data)
            
        except (json.JSONDecodeError, ValueError) as e:
            raise ValueError(f"Failed to parse question from response: {e}\nResponse: {content}")