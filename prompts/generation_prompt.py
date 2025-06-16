import json
from typing import List, Dict, Any

FEW_SHOT_EXAMPLES = [
    {
        "question": "The perimeter of an isosceles triangle is 83 inches. Each of the two congruent sides of the triangle has a length of 24 inches. What is the length, in inches, of the third side?",
        "choices": {
            "A": "35",
            "B": "39",
            "C": "43",
            "D": "47"
        },
        "answer": "A"
    },
    {
        "question": "A shipping company charged a customer $25 to ship some small boxes and some large boxes. The equation above represents the relationship between a, the number of small boxes, and b, the number of large boxes, the customer had shipped. If the customer had 3 small boxes shipped, how many large boxes were shipped?",
        "choices": {
            "A": "3",
            "B": "4",
            "C": "5",
            "D": "6"
        },
        "answer": "C"
    },
    {
        "question": "If f is the function defined by f(x) = 2x - 1 / 3, what is the value of f(5)?",
        "choices": {
            "A": "4/3",
            "B": "7/3",
            "C": "3",
            "D": "9"
        },
        "answer": "C"
    },
    {
        "question": "A bakery sells trays of cookies. Each tray contains at least 50 cookies but no more than 60. Which of the following could be the total number of cookies on 4 trays of cookies?",
        "choices": {
            "A": "165",
            "B": "205",
            "C": "245",
            "D": "285"
        },
        "answer": "B"
    },
    {
        "question": "y = 4x - 9; y = 19; What is the solution (x, y) to the given system of equations?",
        "choices": {
            "A": "(4,19)",
            "B": "(7,19)",
            "C": "(19,4)",
            "D": "(19,7)"
        },
        "answer": "C"
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
Your goal is to generate {count} high-quality, text-only SAT math question(s) that are indistinguishable from official College Board question.

The questions should fall in one of the following topics:
<topics>
- linear equations in one variable (e.g. What value of satisfies the equation 5p + 180 = 250?)
- linear equations in two variables (e.g. Line k is defined by y = 3x + 15. Line j is perpendicular to line k in the xy-plane. What is the slope of line j?)
- linear functions (e.g. The front of a roller-coaster car is at the bottom of a hill and is 15 feet above the ground. If the front of the roller-coaster car rises at a constant rate of 8 feet per second, which of the following equations gives the height h, in feet, of the front of the roller-coaster car s seconds after it starts up the hill?)
- linear inequalities (e.g. Valentina bought two containers of beads. In the first container 30% of the beads are red, and in the second container 70% of the beads are red.  Together, the containers have at least 400 red beads. Which inequality shows this relationship, where x is the total number of beads in the first container and y is the total number of beads in the second container?)
- systems of linear equations (e.g. y = 2x + 3; x = 1; What is the solution (x, y) to the given system of equations?)
</topics>

Follow this process:
1. Randomly select one of the topics
2. Generate a question that is related to the topic. It should only contain numbers and basic arithmetic operations.
3. Generate a correct answer choice. Explain why it is correct.
4. Generate 3 incorrect answer choices. For each incorrect answer choice, explain why it is incorrect.
5. Output the question and answer choices in the following JSON array format:
<format>
[
    {{"question": "...", "choices": {{"A": "...", "B": "...", "C": "...", "D": "..."}}, "answer": "..."}},
    {{"question": "...", "choices": {{"A": "...", "B": "...", "C": "...", "D": "..."}}, "answer": "..."}}
]
</format>

Here are some examples:
<examples>
{examples_text}
</examples>

Generate exactly {count} question(s), and do not output anything else besides the JSON array."""
    
    return prompt