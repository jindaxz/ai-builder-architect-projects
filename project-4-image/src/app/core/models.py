from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    image_base64: str = Field(..., description="Base64-encoded image data")
    question: Optional[str] = Field(None, description="Optional question to answer about the image")
    modes: List[Literal["describe", "tags", "qa", "ocr"]] = Field(
        default_factory=lambda: ["describe", "tags"],
        description="Pipeline steps to execute",
    )


class Detection(BaseModel):
    label: str
    confidence: float
    box: List[int] = Field(..., description="[x1, y1, x2, y2]")


class AnalyzeResponse(BaseModel):
    summary: str
    tags: List[str]
    answer: Optional[str] = None
    ocr_text: Optional[str] = None
    detections: List[Detection] = Field(default_factory=list)
    model_used: str
    artifacts_path: Optional[str] = None
