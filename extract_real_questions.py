#!/usr/bin/env python3
import os
import json
import base64
import click
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
    prompt = """Please analyze this SAT math practice PDF and extract ALL questions into JSON format.

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

    try:
        # Use PDF analysis (note: this requires the file to be uploaded to Anthropic)
        # For now, we'll simulate by asking to analyze the PDF content
        response = client.messages.create(
            model="claude-3-7-sonnet-latest",
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


@click.command()
@click.option('--input-dir', '-i', type=click.Path(exists=True), default='data/Algebra',
              help='Directory containing PDF files')
@click.option('--output', '-o', type=click.Path(), default='data/real_questions.json',
              help='Output JSON file')
@click.option('--limit', '-l', type=int, help='Limit number of PDFs to process')
def main(input_dir, output, limit):
    """Extract SAT questions from PDF files"""
    
    try:
        # Initialize Anthropic client
        client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        
        # Get all PDF files
        pdf_files = get_pdf_files(input_dir)
        
        click.echo(f"Found {len(pdf_files)} PDF files in {input_dir}")
        
        if limit:
            pdf_files = pdf_files[:limit]
            click.echo(f"Processing first {limit} files")
        
        all_questions = []
        
        # Process each PDF
        for pdf_file in pdf_files:
            click.echo(f"\nProcessing: {pdf_file}")
            questions = extract_questions_from_pdf(client, pdf_file)
            click.echo(f"Extracted {len(questions)} questions")
            all_questions.extend(questions)
        
        # Save to JSON
        output_dir = os.path.dirname(output)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        with open(output, 'w', encoding='utf-8') as f:
            json.dump(all_questions, f, indent=2, ensure_ascii=False)
        
        click.echo(f"\nSaved {len(all_questions)} questions to {output}")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()


if __name__ == "__main__":
    main()