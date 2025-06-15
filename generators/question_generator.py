import json
import os
from typing import Optional, List
from anthropic import Anthropic
from dotenv import load_dotenv

from models.question import Question
from prompts.generation_prompt import GENERATION_SYSTEM_PROMPT, FEW_SHOT_EXAMPLES

load_dotenv()


class QuestionGenerator:
    def __init__(self, api_key: Optional[str] = None):
        self.client = Anthropic(api_key=api_key or os.getenv("ANTHROPIC_API_KEY"))
        
    def generate_questions(self, count: int = 1) -> List[Question]:
        """Generate multiple SAT math questions in a single API call"""
        
        # Build few-shot examples
        examples_text = "Here are some example SAT questions:\n\n"
        for i, example in enumerate(FEW_SHOT_EXAMPLES, 1):
            examples_text += f"Example {i}:\n"
            examples_text += json.dumps(example, indent=2)
            examples_text += "\n\n"
        
        if count == 1:
            prompt = f"{examples_text}Now generate a new SAT math question following the same format. Make it unique and different from the examples."
        else:
            prompt = f"""{examples_text}Now generate {count} new SAT math questions following the same format. 
Make each question unique and cover different topics (linear equations, quadratics, systems of equations, functions, word problems, or basic statistics).

Output the questions as a JSON array, like this:
[
    {{"content": "...", "choices": {{"A": "...", "B": "...", "C": "...", "D": "..."}}, "correct_answer": "..."}},
    {{"content": "...", "choices": {{"A": "...", "B": "...", "C": "...", "D": "..."}}, "correct_answer": "..."}}
]

Generate exactly {count} questions."""
        
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