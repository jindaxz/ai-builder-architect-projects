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

    content = response.get("message", {}).get("content", "")
    if not content:
        raise RuntimeError("Empty response from Ollama")
    return content, model
