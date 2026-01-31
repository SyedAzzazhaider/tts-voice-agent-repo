# Member 5 – ABBAS: Backend Integration & API

**Role:** Backend Integration & API Engineer  
**Responsibilities:**
- Connect all modules together
- Build Flask / FastAPI APIs
- Serve as the bridge between Frontend ↔ Backend
- Ensure real-time responses

**Tools:** Flask, Python, REST APIs

---

## Why this is important

Frontend and AI modules cannot function or connect without this API layer. The API wires:

- **Module 1** – Text Input  
- **Module 2** – File Extractor (PDF/DOCX)  
- **Module 3** – OCR Engine (images)  
- **Module 4** – Language Detection  
- **Module 5** – TTS Engine  

into a single REST API that the frontend can call.

---

## Quick start

1. **Install dependencies**

   - **Option A – Minimal (no OCR, no Rust/torch):** Use when `requirements.txt` fails (e.g. Python 3.13, Rust not installed). Text + file + TTS work; OCR returns “not available”.
     ```bash
     pip install -r requirements_minimal.txt
     ```
   - **Option B – Full:** If you need OCR (images), install the full stack (may require Rust on some setups):
     ```bash
     pip install -r requirements.txt
     pip install -r api_requirements.txt
     ```

2. **Run the API server:**
   ```bash
   python run_api.py
   ```
   Server runs at **http://127.0.0.1:5000**

3. **Check health:**
   ```bash
   curl http://127.0.0.1:5000/api/v1/health
   ```

---

## REST API endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/health` | Health check |
| POST | `/api/v1/text/process` | Process raw text (Module 1) |
| POST | `/api/v1/extract/file` | Extract text from PDF/DOCX (Module 2) |
| POST | `/api/v1/extract/image` | OCR from image (Module 3) |
| POST | `/api/v1/language/detect` | Detect language (Module 4) |
| POST | `/api/v1/tts/generate` | Generate speech (Module 5) |
| POST | `/api/v1/pipeline` | **Full pipeline**: extract → detect → TTS (real-time) |
| GET | `/api/v1/audio/<filename>` | Serve generated audio for playback |

---

## Full pipeline (real-time)

**POST `/api/v1/pipeline`**

One request that: extracts text (from text/file/image) → detects language → generates speech → returns audio URL.

**JSON body examples:**

- **Text input:**
  ```json
  { "input_type": "text", "text": "Hello world" }
  ```

- **File (path):**
  ```json
  { "input_type": "file", "file_path": "C:/path/to/document.pdf" }
  ```

- **Image (path):**
  ```json
  { "input_type": "image", "image_path": "C:/path/to/image.png" }
  ```

**Form-data (uploads):**
- `input_type=file` + `file` = PDF/DOCX file  
- `input_type=image` + `image` = image file  

**Success response (real-time):**
```json
{
  "success": true,
  "text_preview": "...",
  "char_count": 42,
  "language": "en",
  "language_name": "English",
  "audio_url": "/api/v1/audio/audio_en_abc123.mp3",
  "filename": "audio_en_abc123.mp3"
}
```

Frontend can play audio via: `GET http://127.0.0.1:5000/api/v1/audio/<filename>`.

---

## Project layout (Member 5)

- `api/` – Backend integration & API
  - `app.py` – Flask app, routes, CORS, serve audio
  - `services.py` – Pipeline service connecting all modules
  - `README_MEMBER5.md` – This file
- `run_api.py` – Script to start the API server

No other project files are modified; this is an additive API layer.
