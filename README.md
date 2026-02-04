# 🎤 TTS Voice Agent - Multilingual Text-to-Speech System

A real-time Text-to-Speech system supporting **English** and **Urdu** with multiple input formats (text, PDF, DOCX, images). Built with Flask API and modern web interface.

---

## ✨ Features

- **Multi-format Input**: Text, PDF, DOCX, and images (OCR)
- **Bilingual Support**: Automatic English and Urdu detection
- **Dual-mode Operation**: Online (high-quality) and offline (fallback)
- **Real-time Processing**: Sub-second audio generation
- **RESTful API**: Complete backend with CORS support
- **Web Interface**: Modern, responsive UI

---

## 🛠️ Technology Stack

**Backend:** Python 3.10+, Flask 2.3+, Flask-CORS  
**TTS Engines:** Edge TTS (online), pyttsx3 (offline)  
**Text Extraction:** PyPDF2, pdfplumber, python-docx, EasyOCR  
**AI/ML:** PyTorch 2.6+, langdetect, OpenCV  
**Frontend:** HTML5, CSS3, JavaScript

---

## 📦 Installation

### Prerequisites
- Python 3.10+
- 4GB+ RAM (for OCR models)

### Setup
```bash
# Clone repository
git clone <repository-url>
cd tts-voice-agent-repo

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate  # Windows
source venv/bin/activate  # Linux/macOS

# Install dependencies
pip install -r requirements.txt
```

**Note:** First installation downloads ~2GB of AI models (PyTorch, OCR).

---

## 🚀 Usage

### Start Web Interface
```bash
python run_api.py
```
Open browser: **http://127.0.0.1:5000/app**

### Start CLI Interface
```bash
python run_cli.py
```

---

## 📡 API Documentation

### Base URL
```
http://127.0.0.1:5000/api/v1
```

### Main Endpoint - Full Pipeline

**POST** `/api/v1/pipeline`

**Text Input:**
```json
{
  "input_type": "text",
  "text": "Hello world"
}
```

**File Upload:**
```http
Content-Type: multipart/form-data

input_type: file
file: <PDF/DOCX file>
```

**Image Upload:**
```http
Content-Type: multipart/form-data

input_type: image
image: <image file>
```

**Success Response:**
```json
{
  "success": true,
  "text_preview": "Hello world",
  "language": "en",
  "language_name": "English",
  "audio_url": "/api/v1/audio/audio_en_abc123.mp3",
  "filename": "audio_en_abc123.mp3"
}
```

### Other Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/health` | Health check |
| POST | `/api/v1/text/process` | Process text (Module 1) |
| POST | `/api/v1/extract/file` | Extract from PDF/DOCX (Module 2) |
| POST | `/api/v1/extract/image` | OCR from image (Module 3) |
| POST | `/api/v1/language/detect` | Detect language (Module 4) |
| POST | `/api/v1/tts/generate` | Generate speech (Module 5) |
| GET | `/api/v1/audio/<filename>` | Stream audio file |

### Example (cURL)
```bash
curl -X POST http://127.0.0.1:5000/api/v1/pipeline \
  -H "Content-Type: application/json" \
  -d '{"input_type": "text", "text": "Hello world"}'
```

---

## 📁 Project Structure

```
tts-voice-agent-repo/
├── api/                    # Backend API
│   ├── app.py              # Flask routes
│   └── services.py         # Business logic
├── frontend/               # Web interface
│   ├── index.html
│   ├── style.css
│   └── script.js
├── modules/                # Core modules
│   ├── text_input.py       # Text processing
│   ├── file_extractor.py   # PDF/DOCX extraction
│   ├── ocr_engine.py       # Image OCR
│   ├── language_detector.py # Language detection
│   └── tts_engine.py       # Speech generation
├── assets/                 # Audio output
├── samples/                # Test files
├── config.py               # Configuration
├── requirements.txt        # Dependencies
├── run_api.py              # API server
├── run_cli.py              # CLI interface
└── README.md
```

---

## 🧪 Testing

### Manual Testing

1. Start server: `python run_api.py`
2. Open: `http://127.0.0.1:5000/app`
3. Test:
   - English text: "Hello world"
   - Urdu text: "السلام علیکم"
   - Upload PDF/DOCX
   - Upload image for OCR

### Automated Testing
```bash
pytest                    # Run tests
pytest --cov=modules      # With coverage
```

---

## 🚢 Deployment

### Production Setup

**Using Gunicorn (Linux):**
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 "api.app:create_app()"
```

**Using Waitress (Windows):**
```bash
pip install waitress
waitress-serve --host=0.0.0.0 --port=5000 api.app:app
```

### Production Checklist
- Set `FLASK_DEBUG=False`
- Use production WSGI server
- Configure reverse proxy (Nginx)
- Enable HTTPS
- Set up monitoring and logging

---

## ⚙️ Configuration

Create `.env` file (optional):
```env
APP_NAME=TTS Voice Agent
SUPPORTED_LANGUAGES=en,ur
MAX_FILE_SIZE_MB=10
AUDIO_FORMAT=mp3
TTS_ENGINE=edge
FLASK_PORT=5000
```

---

## 🔧 Troubleshooting

**Flask not found:**
```bash
.\venv\Scripts\Activate  # Activate venv first
```

**OCR slow on first run:**
- Downloads models (~1GB) once
- Subsequent requests are fast

**Audio not playing:**
- Check browser console
- Try Chrome/Firefox
- Verify file in `assets/` folder

**TTS Quality Issues:**
- **Online (Tier 1):** Uses Edge TTS (Human-like). Requires stable internet.
- **Offline (Tier 2):** Uses MMS Neural Model (Human-like). First run per language takes ~1-2 min to download model.
- **Offline (Tier 3):** Uses `pyttsx3` (Robotic). Only occurs if Tier 1 & 2 fail.

---

## 📄 System Requirements

- **CPU:** 2+ cores recommended
- **RAM:** 4GB minimum (8GB for OCR)
- **Disk:** 3GB for dependencies
- **OS:** Windows 10+, Linux, macOS
- **Browser:** Chrome 90+, Firefox 88+

---

## 🔄 Version

**v1.0.0** - Production Release
- Multi-format input (text, PDF, DOCX, images)
- Bilingual TTS (English & Urdu)
- RESTful API with documentation
- Web interface with real-time playback
- Online/offline dual-mode

---

## 📞 Support

For technical support:
- Email: azzazhaider4@example.com
- Documentation: [Attached with the Code]

---

**Built for professional text-to-speech automation**