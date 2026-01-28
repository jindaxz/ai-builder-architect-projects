from __future__ import annotations

import base64
import json
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import List

from PIL import Image

from app.config import get_settings
from app.core.models import AnalyzeRequest, AnalyzeResponse, Detection
from app.core.ollama_client import generate_response


def _decode_image(image_base64: str) -> bytes:
    try:
        return base64.b64decode(image_base64)
    except Exception as exc:  # noqa: BLE001 - propagate as ValueError
        raise ValueError("Invalid base64 image payload") from exc


def _validate_image(image_bytes: bytes) -> None:
    with Image.open(BytesIO(image_bytes)) as img:
        img.verify()


def _build_prompt(request: AnalyzeRequest) -> str:
    modes = ", ".join(request.modes)
    question_part = f"\nQuestion: {request.question}" if request.question else ""
    return (
        "You are a helpful vision assistant working on-device. "
        "Provide grounded observations and keep hallucinations minimal.\n"
        f"Requested modes: {modes}.\n"
        "Describe the scene, list notable objects, and answer the user question if provided."
        f"{question_part}"
    )


def _guess_tags(summary: str, limit: int = 6) -> List[str]:
    seen: List[str] = []
    for token in summary.split():
        normalized = "".join(ch for ch in token.lower().strip(",.()") if ch.isalnum())
        if len(normalized) < 4:
            continue
        if normalized in seen:
            continue
        seen.append(normalized)
        if len(seen) >= limit:
            break
    return seen


async def analyze_image(request: AnalyzeRequest) -> AnalyzeResponse:
    settings = get_settings()

    image_bytes = _decode_image(request.image_base64)
    max_bytes = settings.max_image_mb * 1024 * 1024
    if len(image_bytes) > max_bytes:
        raise ValueError("Image exceeds max size limit")

    _validate_image(image_bytes)

    prompt = _build_prompt(request)
    summary, model_used = await generate_response(prompt, image_bytes)
    tags = _guess_tags(summary)

    artifacts_dir = settings.artifacts_dir
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    job_id = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
    artifact_path = artifacts_dir / f"job-{job_id}.json"

    payload = {
        "request": request.model_dump(),
        "summary": summary,
        "tags": tags,
        "model": model_used,
    }
    artifact_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    return AnalyzeResponse(
        summary=summary,
        tags=tags,
        answer=None,
        ocr_text=None,
        detections=[],
        model_used=model_used,
        artifacts_path=str(artifact_path),
    )
