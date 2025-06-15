import json
from typing import List, Dict, Any


GENERATION_SYSTEM_PROMPT = """You are an expert SAT math question generator. Generate high-quality, text-only SAT math questions that are indistinguishable from official College Board content.

Rules:
1. Create standard 4-option multiple choice questions (A, B, C, D). There should only be one correct answer.
2. Focus on one of these topics: linear equations, quadratics, systems of equations, functions, word problems, or basic statistics
3. Ensure mathematical accuracy - the correct answer must be verifiable
4. Match SAT style and difficulty level
5. Use clear, concise language
6. Avoid complex formatting or special symbols beyond basic math notation

Before you generate anything, randomly select one of the topics.

Output format must be exactly:
{
    "content": "The question text here",
    "choices": {
        "A": "first choice",
        "B": "second choice", 
        "C": "third choice",
        "D": "fourth choice"
    },
    "correct_answer": "B"
}
"""

FEW_SHOT_EXAMPLES = [
    {
        "content": "If 3x + 7 = 22, what is the value of x?",
        "choices": {
            "A": "3",
            "B": "5",
            "C": "7",
            "D": "15"
        },
        "correct_answer": "B"
    },
    {
        "content": "A store offers a 20% discount on all items. If the discounted price of a jacket is $64, what was the original price?",
        "choices": {
            "A": "$51.20",
            "B": "$76.80",
            "C": "$80.00",
            "D": "$84.00"
        },
        "correct_answer": "C"
    },
    {
        "content": "If f(x) = 2x² - 3x + 1, what is f(2)?",
        "choices": {
            "A": "1",
            "B": "3",
            "C": "5",
            "D": "7"
        },
        "correct_answer": "B"
    }
]


def get_generate_questions_prompt(count: int = 1) -> str:
    """Generate the prompt for creating SAT questions"""
    
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
    
    return prompt