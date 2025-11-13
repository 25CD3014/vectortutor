"""
Groq API Client Wrapper
Handles all interactions with Groq API using llama-3.3-70b-versatile model
"""
import os
from groq import Groq
from typing import Optional, List, Dict


class GroqClient:
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Groq client with API key from environment or parameter"""
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        # Initialize Groq client - handle potential proxy issues
        # Some environments may have HTTP_PROXY/HTTPS_PROXY set which can cause issues
        # Temporarily unset proxy env vars if they exist to avoid conflicts
        proxy_vars = {}
        for var in ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']:
            if var in os.environ:
                proxy_vars[var] = os.environ.pop(var)
        
        try:
            # Initialize with just the API key
            self.client = Groq(api_key=self.api_key)
        except (TypeError, ValueError) as e:
            # If there's still an error, try with explicit httpx client
            import httpx
            # Create httpx client without proxy settings
            http_client = httpx.Client()
            self.client = Groq(api_key=self.api_key, http_client=http_client)
        finally:
            # Restore proxy env vars if they were set
            os.environ.update(proxy_vars)
        
        self.model = "llama-3.3-70b-versatile"
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None, 
                 temperature: float = 0.7, max_tokens: int = 4096) -> str:
        """
        Generate text using Groq API
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Sampling temperature (0.0-2.0)
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text response
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Groq API error: {str(e)}")
    
    def generate_json(self, prompt: str, system_prompt: Optional[str] = None,
                     temperature: float = 0.3) -> Dict:
        """
        Generate JSON response (lower temperature for structured output)
        
        Args:
            prompt: User prompt requesting JSON
            system_prompt: Optional system prompt
            temperature: Lower temperature for more deterministic output
            
        Returns:
            Parsed JSON dictionary
        """
        import json
        
        json_prompt = f"{prompt}\n\nRespond with valid JSON only, no additional text."
        response = self.generate(json_prompt, system_prompt, temperature, max_tokens=4096)
        
        # Try to extract JSON from response
        try:
            # Remove markdown code blocks if present
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()
            
            return json.loads(response)
        except json.JSONDecodeError:
            # If JSON parsing fails, try to fix common issues
            try:
                # Remove any leading/trailing text
                start = response.find("{")
                end = response.rfind("}") + 1
                if start >= 0 and end > start:
                    return json.loads(response[start:end])
            except:
                pass
            raise Exception(f"Failed to parse JSON response: {response[:200]}")

