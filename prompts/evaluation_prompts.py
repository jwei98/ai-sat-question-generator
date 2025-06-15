from models.question import Question


def get_accuracy_prompt(question: Question) -> str:
    return f"""You are a mathematics expert tasked with verifying the accuracy of SAT math questions and their answers.

A question/answer pair is considered correct if and only if:
- The given answer is correct
- All other answer choices are incorrect

Return a JSON response describing the correctness of the question/answer pair with this EXACT format:
<json>
{{
    "correct": true or false,
    "explanation": "Brief explanation of your verification on a single line"
}}
</json>

Here is the question and answer:
<question>
{question.question}

Answer Choices:
A) {question.choices['A']}
B) {question.choices['B']}
C) {question.choices['C']}
D) {question.choices['D']}
</question>

<answer>
Stated Correct Answer: {question.answer}
</answer>
"""