def get_extraction_prompt() -> str:
    """Get the prompt for extracting SAT questions from PDFs"""
    
    return """Please analyze this SAT math practice PDF and extract ALL questions into JSON format.

Your process should be:
1. Read each question in the PDF file (each question is on a new page)
2. For each question, determine if it meets the criteria. If it doesn't include a graph, then it is a valid question.
3. If it is a valid question, extract the question ID, the complete question text, and all 4 multiple choice choices. The question should only contain numbers and basic arithmetic operations. Do not use unicode escape sequences.
4. If the question does not have any multiple choice choices, you should generate 4 choices following the instructions below
<instructions_for_generating_choices>
1. Solve the question to get the correct answer. Put your reasoning in <reasoning> tags. Verify that the answer is correct.
2. Generate three incorrect answer choices, and validate that they are incorrect. Put your reasoning in <reasoning> tags.
3. Use the above correct and incorrect choices as the four choices.
</instructions_for_generating_choices>
4. Format your response as a JSON array like so:
<json>
[
    {
        "id": "unique-id-for-this-question",
        "question": "Complete question text here",
        "choices": {
            "A": "First choice",
            "B": "Second choice",
            "C": "Third choice",
            "D": "Fourth choice"
        },
    }
]
</json>
"""