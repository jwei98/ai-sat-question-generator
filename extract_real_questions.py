#!/usr/bin/env python3
import os
import json
import base64
import click
from pathlib import Path
from typing import List, Dict
from anthropic import Anthropic
from dotenv import load_dotenv

from prompts.extraction_prompt import get_extraction_prompt

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
    
    # Get the extraction prompt
    prompt = get_extraction_prompt()

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
        for pdf_file in pdf_files[:1]:
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