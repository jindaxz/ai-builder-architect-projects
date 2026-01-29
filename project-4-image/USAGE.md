# Usage Guide

## Easiest Way - Command Line Tool

No need to start a web server, analyze images directly:

### Basic Usage

```bash
# 1. Make sure virtual environment is activated
source .venv/bin/activate

# 2. 分析图片（最简单的方式）
python scripts/analyze_image.py 你的图片.jpg

# 3. Analyze with a question
python scripts/analyze_image.py your_image.jpg --question "What is in this image?"

# 4. Specify analysis modes
python scripts/analyze_image.py your_image.jpg --modes describe,tags,qa
```

### Parameters

- `image_path`: Image file path (required)
- `--question` or `-q`: Question about the image (optional)
- `--modes` or `-m`: Analysis modes, comma-separated (optional)
  - `describe`: Describe image content
  - `tags`: Generate tags
  - `qa`: Question-answering mode
  - `ocr`: Text recognition

### Examples

```bash
# Example 1: Simple description
python scripts/analyze_image.py photo.jpg

# Example 2: Ask a question
python scripts/analyze_image.py photo.jpg -q "What text is visible in this image?"

# Example 3: Description and tags only
python scripts/analyze_image.py photo.jpg -m describe,tags

# Example 4: Full analysis
python scripts/analyze_image.py photo.jpg -q "Describe this image in detail" -m describe,tags,qa
```

### Output Example

```
Reading image: photo.jpg
Analyzing image...

============================================================
ANALYSIS RESULTS
============================================================

📝 Summary:
This image shows a beautiful sunset over a mountain landscape with vibrant orange and pink colors in the sky...

🏷️  Tags: sunset, mountain, landscape, sky, clouds, nature

🤖 Model used: moondream
💾 Results saved to: artifacts/job-20260127203045123456.json
============================================================
```

## Using Web API (Optional)

If you want to use via HTTP API:

1. **Start the server**
   ```bash
   uvicorn app.main:app --host 127.0.0.1 --port 8810 --reload --app-dir src
   ```

2. **Access API documentation**
   Open your browser and visit: http://127.0.0.1:8810/docs

3. **Test on the web interface**
   - Click on the `/api/v1/analyze` endpoint
   - Click "Try it out"
   - Upload an image or input base64 encoding
   - Click "Execute"

## Frequently Asked Questions

**Q: Getting "image not found" error?**
A: Make sure the image path is correct. You can use absolute or relative paths.

**Q: Analysis is slow?**
A: The first time you use it, the model will be downloaded. After that, it will be much faster. Make sure the Ollama service is running.

**Q: How to view analysis result history?**
A: Results are saved in JSON files under the `artifacts/` directory
