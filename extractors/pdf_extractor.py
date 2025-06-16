import os
import json
import base64
from pathlib import Path
from typing import List, Dict
from anthropic import Anthropic

from prompts.extraction_prompt import get_extraction_prompt


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