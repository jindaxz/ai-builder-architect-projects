from app.config import get_settings


def test_default_models_present():
    settings = get_settings()
    assert "moondream" in settings.ollama_models
