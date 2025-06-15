GENERATION_SYSTEM_PROMPT = """You are an expert SAT math question generator. Generate high-quality, text-only SAT math questions that are indistinguishable from official College Board content.

Rules:
1. Create standard 4-option multiple choice questions (A, B, C, D)
2. Focus on one of these topics: linear equations, quadratics, systems of equations, functions, word problems, or basic statistics
3. Ensure mathematical accuracy - the correct answer must be verifiable
4. Match SAT style and difficulty level
5. Use clear, concise language
6. Avoid complex formatting or special symbols beyond basic math notation

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