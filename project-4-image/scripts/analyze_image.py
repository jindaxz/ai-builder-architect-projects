#!/usr/bin/env python3
"""
Command-line tool to analyze images locally without using the HTTP API.

Usage:
    python scripts/analyze_image.py <image_path> [--question "your question"] [--modes describe,tags,qa]
    
Examples:
    python scripts/analyze_image.py photo.jpg
    python scripts/analyze_image.py photo.jpg --question "What is in this image?"
    python scripts/analyze_image.py photo.jpg --question "What text is visible?" --modes describe,ocr
"""

import argparse
import asyncio
import base64
import sys
from pathlib import Path

# Add src to path so we can import app modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app.core.models import AnalyzeRequest
from app.services.pipeline import analyze_image


def encode_image(image_path: Path) -> str:
    """Read image file and encode to base64."""
    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")
    
    with open(image_path, "rb") as f:
        image_bytes = f.read()
    
    return base64.b64encode(image_bytes).decode("utf-8")


async def main():
    parser = argparse.ArgumentParser(
        description="Analyze an image using local Ollama models",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        "image_path",
        type=Path,
        help="Path to the image file"
    )
    
    parser.add_argument(
        "--question",
        "-q",
        type=str,
        default=None,
        help="Optional question about the image"
    )
    
    parser.add_argument(
        "--modes",
        "-m",
        type=str,
        default="describe,tags",
        help="Comma-separated list of modes: describe, tags, qa, ocr (default: describe,tags)"
    )
    
    args = parser.parse_args()
    
    # Parse modes
    modes = [m.strip() for m in args.modes.split(",") if m.strip()]
    valid_modes = ["describe", "tags", "qa", "ocr"]
    invalid_modes = [m for m in modes if m not in valid_modes]
    if invalid_modes:
        print(f"Error: Invalid modes: {invalid_modes}. Valid modes are: {valid_modes}", file=sys.stderr)
        sys.exit(1)
    
    try:
        # Encode image
        print(f"Reading image: {args.image_path}")
        image_b64 = encode_image(args.image_path)
        
        # Create request
        request = AnalyzeRequest(
            image_base64=image_b64,
            question=args.question,
            modes=modes
        )
        
        # Analyze
        print("Analyzing image...")
        if args.question:
            print(f"Question: {args.question}")
        print()
        
        response = await analyze_image(request)
        
        # Print results
        print("=" * 60)
        print("ANALYSIS RESULTS")
        print("=" * 60)
        print(f"\n📝 Summary:\n{response.summary}\n")
        
        if response.tags:
            print(f"🏷️  Tags: {', '.join(response.tags)}\n")
        
        if response.answer:
            print(f"❓ Answer: {response.answer}\n")
        
        if response.ocr_text:
            print(f"📄 OCR Text:\n{response.ocr_text}\n")
        
        if response.detections:
            print(f"🔍 Detections ({len(response.detections)}):")
            for det in response.detections:
                print(f"  - {det.label} (confidence: {det.confidence:.2f})")
            print()
        
        print(f"🤖 Model used: {response.model_used}")
        if response.artifacts_path:
            print(f"💾 Results saved to: {response.artifacts_path}")
        print("=" * 60)
        
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
