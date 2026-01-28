from fastapi import APIRouter, HTTPException

from app.core.models import AnalyzeRequest, AnalyzeResponse
from app.services.pipeline import analyze_image

router = APIRouter(tags=["analysis"])


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(request: AnalyzeRequest) -> AnalyzeResponse:
    try:
        return await analyze_image(request)
    except ValueError as exc:  # Bad input
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:  # Model/service error
        raise HTTPException(status_code=502, detail=str(exc)) from exc
