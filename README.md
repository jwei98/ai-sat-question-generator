# SAT Question Generator

A CLI tool for generating SAT math questions and evaluating their quality using Claude.

## Features

- **Generate** new SAT-style math questions
- **Evaluate** question accuracy (mathematical correctness)
- **Test** authenticity by comparing to real SAT questions
- **Extract** real SAT questions from PDF files (for authenticity baseline)

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd sat-question-generator

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up API key (optional - can also pass via environment variable)
# Create .env file and add: ANTHROPIC_API_KEY=your-key-here
```

## Quick Start

```bash
# Generate 5 SAT math questions
python main.py generate -n 5 -o questions.json

# Evaluate the mathematical accuracy
python main.py evaluate accuracy -i questions.json

# Test how authentic they appear
python main.py evaluate authenticity -i questions.json
```

## Commands

### Generate Questions

Create new SAT-style math questions.

```bash
python main.py generate -n 10 -o generated.json

Options:
  -n, --count INTEGER  Number of questions to generate [default: 1]
  -o, --output PATH    Output JSON file
  --quiet              Suppress individual question display
  -m, --model TEXT     Claude model to use
```

### Evaluate Accuracy

Check if generated questions are mathematically correct.

```bash
python main.py evaluate accuracy -i questions.json

Options:
  -i, --input PATH     Input JSON file with questions [required]
  -o, --output PATH    Output JSON file with results
  --quiet              Show summary only
  -m, --model TEXT     Claude model to use
```

### Evaluate Authenticity

Test how well generated questions match real SAT question style by comparing them to actual SAT questions.

**Note:** This command requires a dataset of real SAT questions. You can either use the pre-extracted questions in `data/real_questions.json` or extract your own using the `extract` command below.

```bash
python main.py evaluate authenticity -i generated.json

Options:
  -i, --input PATH           Input JSON file with generated questions [required]
  -r, --real-questions PATH  Real questions JSON file [default: data/real_questions.json]
  -o, --output PATH          Output JSON file with results
  -m, --model TEXT           Claude model to use
```

### Extract Questions from PDFs (For Authenticity Baseline)

Extract real SAT questions from PDF files to create a baseline for authenticity evaluation.

```bash
python main.py extract -i data/PDFs -o real_questions.json

Options:
  -i, --input PATH     Input directory containing PDF files [default: data/Algebra]
  -o, --output PATH    Output JSON file [default: data/real_questions.json]
  -l, --limit INTEGER  Limit number of PDFs to process
  -m, --model TEXT     Claude model to use
```

## Common Workflows

### 1. Generate and Evaluate New Questions

```bash
# Generate 20 questions
python main.py generate -n 20 -o batch1.json

# Check mathematical accuracy
python main.py evaluate accuracy -i batch1.json

# Test authenticity against real questions
python main.py evaluate authenticity -i batch1.json
```

### 2. Create Your Own Real Question Dataset (Optional)

If you want to use your own SAT PDFs instead of the pre-extracted questions:

```bash
# Extract questions from your PDF collection
python main.py extract -i data/SAT_PDFs -o data/real_questions.json

# Then use for authenticity evaluation
python main.py evaluate authenticity -i generated.json -r data/real_questions.json
```

### 3. Use Different Claude Models

```bash
# Use a specific model for generation
python main.py generate -n 5 --model claude-3-opus-20240229

# Use a faster model for evaluation
python main.py evaluate accuracy -i questions.json --model claude-3-haiku-20240307
```

## Model Configuration

Default model: `claude-3-7-sonnet-latest`

You can specify a different Claude model using the `--model` flag with any command.

## Output Format

Generated questions follow this structure:

```json
{
  "id": "unique-id",
  "question": "Question text...",
  "choices": {
    "A": "First choice",
    "B": "Second choice",
    "C": "Third choice",
    "D": "Fourth choice"
  },
  "answer": "B"
}
```

## Project Structure

```
sat-question-generator/
├── main.py              # CLI entry point
├── models/              # Data models
├── generators/          # Question generation logic
├── evaluators/          # Accuracy and authenticity evaluation
├── extractors/          # PDF extraction logic
├── prompts/             # AI prompts
├── utils/               # Display and utility functions
└── data/                # Default data directory
```

## Requirements

- Python 3.8+
- Anthropic API key
- PDF files for extraction (optional)

## Attribution

The SAT question PDFs used for extraction were sourced from the [SAT Question Bank PDFs](https://www.reddit.com/r/Sat/comments/1bwg9x1/sat_question_bank_pdfs/) Reddit thread. The data included in this repository contains only Algebra SAT questions extracted from these PDFs for convenience.
