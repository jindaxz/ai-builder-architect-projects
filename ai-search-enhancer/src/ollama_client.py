"""
Ollama API Client
Handles communication with local Ollama instance
"""

import requests
import json
from typing import Optional, Dict, Any
from config import (
    OLLAMA_HOST,
    OLLAMA_MODEL,
    SUMMARY_MAX_TOKENS,
    TEMPERATURE,
    SYSTEM_PROMPT,
    SUMMARY_PROMPT_TEMPLATE
)


class OllamaClient:
    """Client for interacting with Ollama API"""

    def __init__(self, host: str = OLLAMA_HOST, model: str = OLLAMA_MODEL):
        self.host = host.rstrip('/')
        self.model = model
        self.api_url = f"{self.host}/api/generate"

    def check_health(self) -> bool:
        """Check if Ollama is running and accessible"""
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False

    def list_models(self) -> list:
        """Get list of available models"""
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return [model['name'] for model in data.get('models', [])]
            return []
        except requests.RequestException:
            return []

    def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = TEMPERATURE,
        max_tokens: int = SUMMARY_MAX_TOKENS
    ) -> Optional[str]:
        """Generate text using Ollama"""
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            }

            if system:
                payload["system"] = system

            response = requests.post(
                self.api_url,
                json=payload,
                timeout=60
            )

            if response.status_code == 200:
                data = response.json()
                return data.get('response', '').strip()
            else:
                print(f"Ollama error: {response.status_code} - {response.text}")
                return None

        except requests.RequestException as e:
            print(f"Request error: {e}")
            return None

    def summarize_search_results(
        self,
        query: str,
        results: list
    ) -> Dict[str, Any]:
        """Summarize search results using Ollama"""

        # Format results for the prompt
        formatted_results = []
        for i, result in enumerate(results, 1):
            title = result.get('title', 'No title')
            snippet = result.get('snippet', 'No snippet')
            url = result.get('url', '')

            formatted_results.append(
                f"{i}. **{title}**\n"
                f"   {snippet}\n"
                f"   Source: {url}\n"
            )

        results_text = "\n".join(formatted_results)

        # Build prompt
        prompt = SUMMARY_PROMPT_TEMPLATE.format(
            query=query,
            results=results_text
        )

        # Generate summary
        summary = self.generate(
            prompt=prompt,
            system=SYSTEM_PROMPT
        )

        if summary:
            return {
                "success": True,
                "query": query,
                "summary": summary,
                "model": self.model,
                "num_results": len(results)
            }
        else:
            return {
                "success": False,
                "error": "Failed to generate summary",
                "query": query
            }

    def test_connection(self) -> Dict[str, Any]:
        """Test Ollama connection and return status"""
        is_healthy = self.check_health()

        if not is_healthy:
            return {
                "connected": False,
                "error": "Ollama is not running or not accessible",
                "host": self.host
            }

        models = self.list_models()

        if self.model not in models:
            return {
                "connected": True,
                "error": f"Model '{self.model}' not found",
                "available_models": models,
                "host": self.host
            }

        return {
            "connected": True,
            "model": self.model,
            "available_models": models,
            "host": self.host
        }
