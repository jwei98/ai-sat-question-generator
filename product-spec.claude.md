# Text-Based SAT Math Question Generator - Product Specification

## Product Overview

**Vision**: Generate high-quality, text-only SAT math questions that are indistinguishable from official College Board content.

**Success Metrics**: 100% mathematical accuracy, unique questions but indistinguishable from official College Board content.

## Core Features

### UI

To start, we'll just expose this through Python script. No need for UI.

### Question Generation Engine

- **Input Parameters**: None
- **Output**: Complete multiple-choice questions with validated answers
- **Coverage**: Linear equations, quadratics, systems, functions, word problems, basic statistics
- **Format**: Standard 4-option multiple choice matching SAT conventions

### Evaluation Frameworks / Success Metrics

Each has its own prompt:

- **Accuracy Judge**: Automated verification of all answers
- **Authenticity Judge**: Distinguishes generated questions from real SAT questions. Goal: 50% correctly distinguished (coin flip).
- **Similarity Judge**: Ensures that questions are semantically unique from real SAT questions, to prevent overfitting. Goal: no more than 90% similarity.

## Technical Requirements

### Core System

- **Base Model**: claude-sonnet-4-20250514
- **Evaluation Models**: Separate LLMs for generator + each evaluation framework
- **Accuracy**: 100% mathematical accuracy

### API Specifications

```
POST /generate-question
{}

Response:
{
    "id": "uuid",
    "content": "If 3x + 7 = 22, what is the value of x?",
    "choices": { A: 3, B: 5, C: 7, D: 15 },
    "correct_answer": "B",
}
```

```
POST /accuracy
{
    "id": "uuid"
}

Response:
{
    "correct": boolean
}
```

```
POST /authenticity
{
    "id": "uuid"
}

Response:
{
    "guess": "generated" | "real"
}
```

```
POST /similarity
{
    "id": "uuid"
}

Response:
{
    "score": in range [0.00, 1.00]
}
```

### Data Requirements

- **Few-shot Training Data**: 100 official SAT math questions with solutions
- **Authenticity Judge Data**: 100 official SAT math questions
- **Similarity Judge**: 100 official SAT math questions
