import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Union

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables or defaults."""

    app_name: str = "Project 4 Image Analyzer"
    api_prefix: str = "/api/v1"
    ollama_host: str = "http://127.0.0.1:11434"
    # Use Union to prevent pydantic_settings from auto-parsing as JSON
    ollama_models: Union[str, List[str]] = ["moondream"]
    max_image_mb: int = 8
    enable_batch_worker: bool = False

    # Paths
    base_dir: Path = Path(__file__).resolve().parents[2]
    artifacts_dir: Path = base_dir / "artifacts"

    model_config = SettingsConfigDict(env_file=(".env", ".env.local"), env_file_encoding="utf-8")

    @field_validator("ollama_models", mode="before")
    @classmethod
    def parse_ollama_models(cls, v: Any) -> List[str]:
        """Parse ollama_models from JSON string, comma-separated string, or list."""
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            # Try JSON parsing first
            if v.strip().startswith("["):
                try:
                    parsed = json.loads(v)
                    if isinstance(parsed, list):
                        return parsed
                except json.JSONDecodeError:
                    pass
            # Fall back to comma-separated values
            if "," in v:
                return [model.strip() for model in v.split(",") if model.strip()]
            # Single value
            if v.strip():
                return [v.strip()]
        # Default fallback
        return ["moondream"]
    
    @model_validator(mode="after")
    def normalize_ollama_models(self) -> "Settings":
        """Ensure ollama_models is always a list."""
        if not isinstance(self.ollama_models, list):
            self.ollama_models = self.parse_ollama_models(self.ollama_models)
        return self


@lru_cache(1)
def get_settings() -> Settings:
    return Settings()
