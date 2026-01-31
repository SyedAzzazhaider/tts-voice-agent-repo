"""
Member 5 - ABBAS: Backend Integration Service Layer
Connects all modules together into a single pipeline for the API.
Heavy modules (file extractor, OCR) are lazy-loaded so the API can start
even when torch/easyocr are not installed (e.g. Python 3.13, no Rust).
"""

import asyncio
import os
import uuid
from pathlib import Path
from typing import Optional, Literal

# Core imports (needed to start the API)
from modules.text_input import process_text
from modules.language_detector import quick_detect
from modules.tts_engine import TTSEngine


# Use project config for paths
try:
    from config import settings
    ASSETS_DIR = getattr(settings, "ASSETS_DIR", Path(__file__).resolve().parent.parent / "assets")
except Exception:
    ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"

ASSETS_DIR.mkdir(parents=True, exist_ok=True)


def run_async(coro):
    """Run async TTS from sync Flask view."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)


class PipelineService:
    """
    Connects all modules: Text Input, File Extractor, OCR, Language Detection, TTS.
    Used by REST API to serve real-time responses.
    """

    def __init__(self):
        self._tts = TTSEngine()
        self._tts.output_dir = str(ASSETS_DIR)

    # --- Step 1: Text extraction (from text, file, or image) ---

    def get_text_from_input(self, text: str) -> dict:
        """Process direct text input (Module 1)."""
        result = process_text(text)
        if not result.success:
            return {"success": False, "error": result.error, "text": None}
        return {
            "success": True,
            "text": result.text,
            "char_count": result.char_count,
            "word_count": result.word_count,
        }

    def get_text_from_file(self, file_path: str) -> dict:
        """Extract text from PDF/DOCX (Module 2)."""
        try:
            from modules.file_extractor import extract_text as extract_from_file
        except ImportError as e:
            return {
                "success": False,
                "error": f"File extraction not available. Install: PyPDF2, pdfplumber, python-docx. ({e})",
                "text": None,
            }
        result = extract_from_file(file_path)
        if not result.success:
            return {"success": False, "error": result.error, "text": None}
        return {
            "success": True,
            "text": result.text,
            "file_type": result.file_type,
            "page_count": result.page_count,
            "char_count": result.char_count,
        }

    def get_text_from_image(self, image_path: str, language: str = "mixed") -> dict:
        """Extract text from image via OCR (Module 3). Lazy-loaded (needs torch/easyocr)."""
        try:
            from modules.ocr_engine import extract_text_from_image
        except ImportError as e:
            return {
                "success": False,
                "error": f"OCR not available. Install: easyocr, torch, Pillow, opencv-python (see requirements.txt). ({e})",
                "text": None,
            }
        result = extract_text_from_image(image_path, language)
        if not result.success:
            return {"success": False, "error": result.error, "text": None}
        return {
            "success": True,
            "text": result.text,
            "confidence": result.confidence,
            "char_count": getattr(result, "char_count", len(result.text)),
        }

    # --- Step 2: Language detection (Module 4) ---

    def detect_language(self, text: str) -> dict:
        """Detect language: 'en' or 'ur' (Module 4)."""
        lang = quick_detect(text)
        return {
            "success": True,
            "language": lang,
            "language_name": "Urdu (اردو)" if lang == "ur" else "English",
        }

    # --- Step 3: TTS generation (Module 5) ---

    def generate_speech(self, text: str, language: Optional[str] = None) -> dict:
        """Generate speech (Module 5 - TTS). Language: 'en' or 'ur'."""
        if not language:
            language = quick_detect(text)
        lang_voice = "urdu" if language == "ur" else "english"
        filename = f"audio_{language}_{uuid.uuid4().hex[:8]}.mp3"
        try:
            path = run_async(
                self._tts.generate_speech(
                    text,
                    language=lang_voice,
                    filename=filename,
                )
            )
            return {
                "success": True,
                "audio_path": path,
                "audio_url": f"/api/v1/audio/{filename}",
                "language": language,
                "filename": filename,
            }
        except Exception as e:
            return {"success": False, "error": str(e), "audio_path": None}

    # --- Full pipeline (extract → detect → TTS) ---

    def run_pipeline(
        self,
        input_type: Literal["text", "file", "image"],
        text: Optional[str] = None,
        file_path: Optional[str] = None,
        image_path: Optional[str] = None,
    ) -> dict:
        """
        Full pipeline: Extract text → Detect language → Generate speech.
        Real-time response with audio URL for frontend.
        """
        # 1) Get text
        if input_type == "text" and text:
            step1 = self.get_text_from_input(text)
        elif input_type == "file" and file_path:
            step1 = self.get_text_from_file(file_path)
        elif input_type == "image" and image_path:
            step1 = self.get_text_from_image(image_path)
        else:
            return {
                "success": False,
                "error": f"Missing data for input_type={input_type} (text, file_path, or image_path)",
            }

        if not step1.get("success"):
            return {"success": False, "error": step1.get("error", "Extraction failed"), "step": "extract"}

        extracted_text = step1["text"]
        if not (extracted_text and extracted_text.strip()):
            return {"success": False, "error": "No text to process", "step": "extract"}

        # 2) Detect language
        step2 = self.detect_language(extracted_text)
        lang = step2["language"]

        # 3) Generate speech
        step3 = self.generate_speech(extracted_text, language=lang)
        if not step3.get("success"):
            return {
                "success": False,
                "error": step3.get("error", "TTS failed"),
                "step": "tts",
                "text_preview": extracted_text[:100],
                "language": lang,
            }

        return {
            "success": True,
            "text_preview": extracted_text[:200],
            "char_count": len(extracted_text),
            "language": lang,
            "language_name": step2["language_name"],
            "audio_url": step3["audio_url"],
            "audio_path": step3["audio_path"],
            "filename": step3["filename"],
        }
