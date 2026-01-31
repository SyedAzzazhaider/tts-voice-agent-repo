"""
Member 5 - ABBAS: Backend Integration & API
Flask REST API - bridge between Frontend ↔ Backend, connects all modules.
"""

import os
import uuid
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory

from api.services import PipelineService, ASSETS_DIR

# Allowed extensions for uploads (from project config)
ALLOWED_EXTENSIONS_FILE = {"pdf", "docx"}
ALLOWED_EXTENSIONS_IMAGE = {"png", "jpg", "jpeg", "bmp", "tiff", "webp"}
MAX_CONTENT_LENGTH_MB = 10


def create_app():
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH_MB * 1024 * 1024

    # CORS for frontend (enable when frontend is added)
    try:
        from flask_cors import CORS
        CORS(app)
    except ImportError:
        pass

    service = PipelineService()

    # --- Root (so GET / doesn't 404) ---
    @app.route("/", methods=["GET"])
    def index():
        return jsonify({
            "service": "TTS Voice Agent API",
            "docs": "See api/README_MEMBER5.md",
            "health": "/api/v1/health",
            "pipeline": "POST /api/v1/pipeline (input_type: text|file|image)",
        })

    # --- Health / readiness ---
    @app.route("/api/v1/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok", "service": "TTS Voice Agent API"})

    # --- Step-by-step endpoints (for frontend to call individually) ---

    @app.route("/api/v1/text/process", methods=["POST"])
    def text_process():
        """Process raw text (Module 1)."""
        data = request.get_json(silent=True) or {}
        text = data.get("text", "").strip()
        if not text:
            return jsonify({"success": False, "error": "Missing 'text'"}), 400
        result = service.get_text_from_input(text)
        return jsonify(result)

    @app.route("/api/v1/extract/file", methods=["POST"])
    def extract_file():
        """Extract text from PDF/DOCX (Module 2). Upload file or send file_path."""
        file_path = None
        if "file" in request.files:
            f = request.files["file"]
            if f.filename:
                ext = Path(f.filename).suffix.lower().lstrip(".")
                if ext not in ALLOWED_EXTENSIONS_FILE:
                    return jsonify({"success": False, "error": "Only .pdf, .docx allowed"}), 400
                safe_name = f"{uuid.uuid4().hex}{Path(f.filename).suffix}"
                upload_dir = Path(ASSETS_DIR) / "temp"
                upload_dir.mkdir(parents=True, exist_ok=True)
                file_path = str(upload_dir / safe_name)
                f.save(file_path)
        if not file_path:
            data = request.get_json(silent=True) or {}
            file_path = (data.get("file_path") or "").strip()
        if not file_path or not os.path.isfile(file_path):
            return jsonify({"success": False, "error": "Missing file upload or valid file_path"}), 400
        result = service.get_text_from_file(file_path)
        return jsonify(result)

    @app.route("/api/v1/extract/image", methods=["POST"])
    def extract_image():
        """Extract text from image via OCR (Module 3). Upload image or send image_path."""
        image_path = None
        if "image" in request.files:
            f = request.files["image"]
            if f.filename:
                ext = Path(f.filename).suffix.lower().lstrip(".")
                if ext not in ALLOWED_EXTENSIONS_IMAGE:
                    return jsonify({"success": False, "error": "Only image formats allowed"}), 400
                safe_name = f"{uuid.uuid4().hex}{Path(f.filename).suffix}"
                upload_dir = Path(ASSETS_DIR) / "temp"
                upload_dir.mkdir(parents=True, exist_ok=True)
                image_path = str(upload_dir / safe_name)
                f.save(image_path)
        if not image_path:
            data = request.get_json(silent=True) or {}
            image_path = (data.get("image_path") or "").strip()
        if not image_path or not os.path.isfile(image_path):
            return jsonify({"success": False, "error": "Missing image upload or valid image_path"}), 400
        lang = (request.get_json(silent=True) or request.form or {}).get("language", "mixed")
        result = service.get_text_from_image(image_path, language=lang)
        return jsonify(result)

    @app.route("/api/v1/language/detect", methods=["POST"])
    def language_detect():
        """Detect language of text (Module 4)."""
        data = request.get_json(silent=True) or {}
        text = (data.get("text") or "").strip()
        if not text:
            return jsonify({"success": False, "error": "Missing 'text'"}), 400
        result = service.detect_language(text)
        return jsonify(result)

    @app.route("/api/v1/tts/generate", methods=["POST"])
    def tts_generate():
        """Generate speech from text (Module 5). Optional language: en | ur."""
        data = request.get_json(silent=True) or {}
        text = (data.get("text") or "").strip()
        if not text:
            return jsonify({"success": False, "error": "Missing 'text'"}), 400
        lang = (data.get("language") or "").strip() or None
        result = service.generate_speech(text, language=lang)
        return jsonify(result)

    # --- Full pipeline (real-time: one request → text + audio URL) ---

    @app.route("/api/v1/pipeline", methods=["GET", "POST"])
    def pipeline():
        """
        Full pipeline: input_type (text | file | image) + data → extract → detect → TTS.
        Returns audio_url and metadata for frontend. Real-time response.
        GET returns usage (browser visits work).
        """
        if request.method == "GET":
            return jsonify({
                "message": "Use POST with JSON or form. Examples:",
                "text": "POST body: {\"input_type\": \"text\", \"text\": \"Hello world\"}",
                "file": "POST body: {\"input_type\": \"file\", \"file_path\": \"C:\\\\path\\\\to\\\\file.pdf\"} or upload form field 'file'",
                "image": "POST body: {\"input_type\": \"image\", \"image_path\": \"C:\\\\path\\\\to\\\\image.png\"} or upload form field 'image'",
                "curl_example": "curl -X POST http://127.0.0.1:5000/api/v1/pipeline -H \"Content-Type: application/json\" -d \"{\\\"input_type\\\": \\\"text\\\", \\\"text\\\": \\\"Hello\\\"}\"",
            })

        input_type = None
        text = None
        file_path = None
        image_path = None

        if request.is_json:
            data = request.get_json()
            input_type = (data.get("input_type") or "").strip().lower()
            text = (data.get("text") or "").strip()
            file_path = (data.get("file_path") or "").strip()
            image_path = (data.get("image_path") or "").strip()
        else:
            input_type = (request.form.get("input_type") or "").strip().lower()
            text = (request.form.get("text") or "").strip()
            file_path = (request.form.get("file_path") or "").strip()
            image_path = (request.form.get("image_path") or "").strip()

        # Handle file upload for file
        if input_type == "file" and "file" in request.files:
            f = request.files["file"]
            if f.filename:
                ext = Path(f.filename).suffix.lower().lstrip(".")
                if ext in ALLOWED_EXTENSIONS_FILE:
                    safe_name = f"{uuid.uuid4().hex}{Path(f.filename).suffix}"
                    upload_dir = Path(ASSETS_DIR) / "temp"
                    upload_dir.mkdir(parents=True, exist_ok=True)
                    file_path = str(upload_dir / safe_name)
                    f.save(file_path)

        # Handle file upload for image
        if input_type == "image" and "image" in request.files:
            f = request.files["image"]
            if f.filename:
                ext = Path(f.filename).suffix.lower().lstrip(".")
                if ext in ALLOWED_EXTENSIONS_IMAGE:
                    safe_name = f"{uuid.uuid4().hex}{Path(f.filename).suffix}"
                    upload_dir = Path(ASSETS_DIR) / "temp"
                    upload_dir.mkdir(parents=True, exist_ok=True)
                    image_path = str(upload_dir / safe_name)
                    f.save(image_path)

        if input_type not in ("text", "file", "image"):
            return jsonify({"success": False, "error": "input_type must be: text, file, or image"}), 400

        result = service.run_pipeline(
            input_type=input_type,
            text=text or None,
            file_path=file_path or None,
            image_path=image_path or None,
        )
        if not result.get("success"):
            return jsonify(result), 400
        return jsonify(result)

    # --- Serve generated audio (for frontend playback) ---

    @app.route("/api/v1/audio/<filename>", methods=["GET"])
    def serve_audio(filename):
        """Serve generated audio file for frontend (real-time playback)."""
        return send_from_directory(ASSETS_DIR, filename, as_attachment=False)

    return app


# Run with: python -m api.app (or flask --app api.app:create_app run)
app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
