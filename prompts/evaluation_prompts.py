from models.question import Question


def get_accuracy_prompt(question: Question) -> str:
    return f"""You are a mathematics expert tasked with verifying the accuracy of SAT math questions and their answers.

A question/answer pair is considered correct if and only if:
- The given answer is correct
- All other answer choices are incorrect

Your verification process should be:
<verification_process>
1. Verify if the given answer is correct, and why.
2. Verify one by one if all other answer choices are incorrect, and why.
3. If the answer is correct and all other answer choices are incorrect, return true. Otherwise, return false.
</verification_process>

Return a JSON response describing the correctness of the question/answer pair with this EXACT format:
<json>
{{
    "correct": true or false,
    "explanation": "Summary of your verification process"
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