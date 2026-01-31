"""
Member 5 - ABBAS: Run the Backend API server
Start the Flask REST API (bridge Frontend ↔ Backend).

Usage:
  python run_api.py

Then call:
  GET  http://127.0.0.1:5000/api/v1/health
  POST http://127.0.0.1:5000/api/v1/pipeline  (JSON: input_type, text | file_path | image_path)
  POST http://127.0.0.1:5000/api/v1/tts/generate
  etc.
"""

import sys
from pathlib import Path

# Ensure project root is on path
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from api.app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
