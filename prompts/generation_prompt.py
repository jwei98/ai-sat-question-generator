import json
from typing import List, Dict, Any

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
    examples_text = ""
    for i, example in enumerate(FEW_SHOT_EXAMPLES, 1):
        examples_text += f"<example {i}>\n"
        examples_text += json.dumps(example, indent=2)
        examples_text += "\n</example>\n"

    prompt = f"""
You are an expert SAT math question generator.
Your goal is to generate {count} high-quality, text-only SAT math question(s) that are indistinguishable from official College Board content.

The questions should fall in one of the following topics:
<topics>
- linear equations
- quadratics
- systems of equations
- functions
- word problems
- basic statistics
</topics>

Follow this process:
1. Randomly select one of the topics
2. Generate a question that is related to the topic
3. Generate the correct answer choice
3. Generate 3 incorrect answer choices
5. Output the question and answer choices in the following format:
<format>
[
    {{"content": "...", "choices": {{"A": "...", "B": "...", "C": "...", "D": "..."}}, "correct_answer": "..."}},
    {{"content": "...", "choices": {{"A": "...", "B": "...", "C": "...", "D": "..."}}, "correct_answer": "..."}}
]
</format>

Here are some examples:
<examples>
{examples_text}
</examples>

Generate exactly {count} question(s)."""
    
    return prompt