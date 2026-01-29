from fastapi import FastAPI

from app.config import get_settings
from app.api.routes import analysis

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Local image content analysis service built on compact Ollama models.",
)

app.include_router(analysis.router, prefix=settings.api_prefix)


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name}
