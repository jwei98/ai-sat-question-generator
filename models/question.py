import uuid
from typing import Dict
from pydantic import BaseModel, Field, field_validator


class Question(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    question: str
    choices: Dict[str, str]
    answer: str

    @field_validator('choices')
    def validate_choices(cls, v):
        if len(v) != 4:
            raise ValueError("Must have exactly 4 choices")
        valid_keys = {'A', 'B', 'C', 'D'}
        if set(v.keys()) != valid_keys:
            raise ValueError("Choices must be labeled A, B, C, D")
        return v

    @field_validator('answer')
    def validate_answer(cls, v, info):
        if 'choices' in info.data and v not in info.data['choices']:
            raise ValueError(f"Correct answer {v} must be one of the choices")
        return v

    def format_for_display(self) -> str:
        """Format question for display"""
        lines = [self.question, ""]
        for key in sorted(self.choices.keys()):
            lines.append(f"{key}) {self.choices[key]}")
        return "\n".join(lines)