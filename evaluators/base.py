import json
import os
from typing import Optional, Dict, Any
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()


class BaseEvaluator:
    """Base class for all evaluators"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.client = Anthropic(api_key=api_key or os.getenv("ANTHROPIC_API_KEY"))
    
    def parse_json_response(self, content: str) -> Dict[str, Any]:
        """
        Extract and parse JSON from LLM response.
        
        Args:
            content: Raw response text from LLM
            
        Returns:
            Parsed JSON dictionary
            
        Raises:
            ValueError: If JSON cannot be parsed
        """
        try:
            # Find JSON in the response
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            
            if start_idx == -1 or end_idx == 0:
                raise ValueError("No JSON object found in response")
            
            json_str = content[start_idx:end_idx]
            
            # Clean up the JSON string - remove any line breaks within string values
            import re
            json_str = re.sub(r'"\s*:\s*"[^"]*\n[^"]*"', lambda m: m.group(0).replace('\n', ' '), json_str)
            
            return json.loads(json_str)
            
        except (json.JSONDecodeError, ValueError) as e:
            raise ValueError(f"Failed to parse JSON from response: {e}")
    
    def call_api(self, prompt: str, max_tokens: int = 2000) -> str:
        """
        Make an API call to the LLM.
        
        Args:
            prompt: The prompt to send
            max_tokens: Maximum tokens in response
            
        Returns:
            Raw response content
        """
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=max_tokens,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        return response.content[0].text