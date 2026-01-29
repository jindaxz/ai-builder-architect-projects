from __future__ import annotations

import base64
from typing import Tuple

from ollama import AsyncClient

from app.config import get_settings


async def generate_response(prompt: str, image_bytes: bytes) -> Tuple[str, str]:
    """Send the prompt + image to Ollama and return (content, model_used)."""

    settings = get_settings()
    if not settings.ollama_models:
        raise RuntimeError("No Ollama models configured")

    model = settings.ollama_models[0]
    client = AsyncClient(host=settings.ollama_host)
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")

    try:
        response = await client.chat(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                    "images": [image_b64],
                }
            ],
        )
    except Exception as e:
        raise RuntimeError(f"Ollama API error: {e}") from e

    # Debug: print response structure if empty
    if not response:
        raise RuntimeError(f"Empty response from Ollama. Response: {response}")
    
    # Try different response formats
    content = None
    if isinstance(response, dict):
        # Try standard format
        content = response.get("message", {}).get("content", "")
        # Try alternative format (some Ollama versions)
        if not content:
            content = response.get("content", "")
        # Try direct message format
        if not content and "message" in response:
            msg = response["message"]
            if isinstance(msg, dict):
                content = msg.get("content", "")
            elif isinstance(msg, str):
                content = msg
    
    if not content:
        raise RuntimeError(
            f"Empty response from Ollama. "
            f"Response structure: {type(response)}, "
            f"Response keys: {list(response.keys()) if isinstance(response, dict) else 'N/A'}, "
            f"Full response: {response}"
        )
    
    return content, model
