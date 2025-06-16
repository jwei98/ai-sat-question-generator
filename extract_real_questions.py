#!/usr/bin/env python3
import os
import json
import base64
from pathlib import Path
from typing import List, Dict
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()


def get_pdf_files(directory: str) -> List[Path]:
    """Get all PDF files from the directory and subdirectories"""
    pdf_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.pdf'):
                pdf_files.append(Path(root) / file)
    return pdf_files


def extract_questions_from_pdf(client: Anthropic, pdf_path: Path) -> List[Dict]:
    """Extract SAT questions from a PDF using Anthropic's API"""
    
    # Read PDF file
    with open(pdf_path, 'rb') as f:
        pdf_content = f.read()
    
    # Create the prompt
    prompt = """Please analyze this SAT math practice PDF and extract questions that meet these criteria:
1. Text-only questions (no graphs, figures, or images required to solve)
2. Multiple choice format with exactly 4 options (A, B, C, D)
3. Clear correct answer provided

For each qualifying question, extract:
- The complete question text
- All 4 answer choices
- The correct answer letter

Format your response as a JSON array like this:
[
    {
        "question": "Complete question text here",
        "choices": {
            "A": "First choice",
            "B": "Second choice",
            "C": "Third choice",
            "D": "Fourth choice"
        },
        "answer": "B"
    }
]

Only include questions that can be fully understood and solved with text alone. Skip any questions that reference graphs, figures, tables, or diagrams."""

    try:
        # Use PDF analysis (note: this requires the file to be uploaded to Anthropic)
        # For now, we'll simulate by asking to analyze the PDF content
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4000,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "document",
                            "source": {
                                "type": "base64",
                                "media_type": "application/pdf",
                                "data": base64.b64encode(pdf_content).decode('utf-8')
                            }
                        }
                    ]
                }
            ]
        )
        
        # Extract JSON from response
        content = response.content[0].text
        start_idx = content.find('[')
        end_idx = content.rfind(']') + 1
        
        if start_idx == -1 or end_idx == 0:
            print(f"No valid JSON found in response for {pdf_path}")
            return []
            
        json_str = content[start_idx:end_idx]
        questions = json.loads(json_str)
        
        return questions
        
    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")
        return []


def main():
    # Initialize Anthropic client
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    # Get all PDF files
    data_dir = "data/Algebra"
    pdf_files = get_pdf_files(data_dir)
    
    print(f"Found {len(pdf_files)} PDF files")
    
    all_questions = []
    
    # Process each PDF
    for pdf_file in pdf_files:
        print(f"\nProcessing: {pdf_file}")
        questions = extract_questions_from_pdf(client, pdf_file)
        print(f"Extracted {len(questions)} questions")
        all_questions.extend(questions)
        
        # Stop if we have enough questions
        if len(all_questions) >= 10:
            break
    
    # Take only the first 10 questions
    selected_questions = all_questions[:10]
    
    # Save to JSON
    output_file = "data/real_questions.json"
    os.makedirs("data", exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(selected_questions, f, indent=2)
    
    print(f"\nSaved {len(selected_questions)} questions to {output_file}")
    
    # Display summary
    for i, q in enumerate(selected_questions, 1):
        print(f"\nQuestion {i}: {q['question'][:100]}...")
        print(f"Correct answer: {q['answer']}")


if __name__ == "__main__":
    main()