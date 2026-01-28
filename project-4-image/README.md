# Project 4 – Image Content Analysis (Ollama Edition)

Local-first image reasoning pipeline that stitches together lightweight vision models served via Ollama, classical detectors, and OCR tools to mimic GPT-4o-style capabilities without remote APIs.

## Getting Started

1. **Prerequisites**
   - macOS / Linux with Python 3.11+
   - [Ollama](https://ollama.ai) installed and running
   - Optional: Homebrew for installing PaddleOCR/Tesseract dependencies

2. **Install dependencies**
   ```bash
   cd project-4-image
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Pull lightweight vision models (default = moondream 1.8B)**
   ```bash
   ./scripts/bootstrap_models.sh            # pulls moondream by default
   # Need a different model? e.g. ./scripts/bootstrap_models.sh llava:7b
   ```

> 💡 `moondream` (~1.8B) is the lightest option available via Ollama today and works on low-RAM, iGPU-only machines. Add multiple models to `.env` if you want fallbacks.

4. **Run the API（默认 127.0.0.1:8810，避开 8000 冲突）**
   ```bash
   uvicorn app.main:app --host 127.0.0.1 --port 8810 --reload --app-dir src
   ```
   > 若 8810 仍被占用，可把 `--port` 改成任意未使用端口（如 8811、8820 等）。

5. **Test**
   ```bash
   pytest
   ```

See `docs/project-4-image-content-analysis-plan.md` for the detailed roadmap.
