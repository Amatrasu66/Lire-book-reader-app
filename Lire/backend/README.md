# 📖 Book Listener — Backend API

> Convert any PDF or TXT book into a streamable audiobook in seconds.  
> Built with Flask · gTTS · PyPDF2

---

## Features

- **PDF & TXT upload** with file-type validation and 32 MB size cap
- **Text extraction** — multi-page PDFs and plain-text files
- **Text-to-Speech** via Google TTS (gTTS) — free, no API key needed
- **Male / Female voice simulation** (speed-based proxy — swappable for ElevenLabs)
- **MP3 streaming** with HTTP Range request support (browser seek works)
- **Automatic cleanup** — temp files expire after 2 hours
- **CORS enabled** — ready for any frontend framework
- **JSON API** — consistent success/error responses throughout
- **Modular architecture** — built for SaaS expansion

---

## Project Structure

```
book_listener/
│
├── app.py              ← Flask app factory & entry point
├── config.py           ← All configurable values
├── requirements.txt
├── README.md
│
├── uploads/            ← Temporary upload storage (auto-created)
├── audio/              ← Generated MP3 files (auto-created)
├── static/             ← Future: serve frontend assets
│
├── routes/
│   ├── __init__.py
│   └── upload_routes.py  ← /upload, /audio/<file>, /cleanup, /health
│
└── utils/
    ├── __init__.py
    ├── pdf_parser.py     ← PyPDF2 text extraction
    ├── txt_parser.py     ← Plain-text reading with encoding fallback
    ├── tts_engine.py     ← gTTS wrapper (engine-agnostic interface)
    └── file_manager.py   ← Directory setup, validation, cleanup
```

---

## Requirements

- Python 3.12 or higher
- pip
- Internet connection (gTTS calls the Google TTS API)

---

## Installation & Setup

### 1. Clone or create the project folder

```bash
git clone <your-repo-url> book_listener
cd book_listener
```

### 2. Create a virtual environment

```bash
# macOS / Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Flask server

```bash
python app.py
```

The API will start on `http://0.0.0.0:5000`.

For production, use Gunicorn:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 "app:app"
```

---

## Environment Variables (optional overrides)

| Variable        | Default   | Description                        |
|----------------|-----------|-------------------------------------|
| `FLASK_DEBUG`  | `true`    | Enable debug mode                  |
| `FLASK_HOST`   | `0.0.0.0` | Host to bind                       |
| `FLASK_PORT`   | `5000`    | Port to bind                       |

---

## API Documentation

### `POST /upload`

Upload a PDF or TXT file. The backend extracts text, converts it to speech, and returns an audio URL.

**Request** — `multipart/form-data`

| Field        | Type   | Required | Description                          |
|-------------|--------|----------|---------------------------------------|
| `file`      | File   | ✅        | PDF or TXT file (max 32 MB)          |
| `voice_type`| String | ❌        | `"female"` (default) or `"male"`     |

**Success Response — 200**

```json
{
  "success": true,
  "audio_url": "/audio/3f8a2b1c4d5e6f7a8b9c0d1e2f3a4b5c.mp3",
  "file_id": "3f8a2b1c4d5e6f7a8b9c0d1e2f3a4b5c",
  "message": "Audio generated successfully."
}
```

**Error Responses**

| Code | Meaning                                      |
|------|----------------------------------------------|
| 400  | No file field / empty filename              |
| 413  | File exceeds 32 MB limit                    |
| 415  | Unsupported file type                       |
| 422  | File is empty, encrypted, or unreadable     |
| 500  | TTS or filesystem failure                   |

```json
{
  "success": false,
  "error": "File type not allowed. Accepted types: pdf, txt"
}
```

---

### `GET /audio/<filename>`

Stream a generated MP3 file.

```
GET /audio/3f8a2b1c4d5e6f7a8b9c0d1e2f3a4b5c.mp3
```

- Returns the audio with `Content-Type: audio/mpeg`
- Supports HTTP Range requests → browser `<audio>` seeking works out of the box
- Returns 404 JSON if the file doesn't exist

---

### `POST /cleanup`

Delete uploaded and audio files older than 2 hours.

```json
{
  "success": true,
  "removed": {
    "uploads_deleted": 3,
    "audio_deleted": 7
  },
  "message": "Cleanup completed."
}
```

> **Note:** In production, protect this endpoint with admin authentication.

---

### `GET /health`

Liveness probe for Docker / load balancers.

```json
{
  "status": "ok",
  "service": "book-listener-api"
}
```

---

## Example API Requests

### cURL

```bash
# Upload a PDF with female voice (default)
curl -X POST http://localhost:5000/upload \
     -F "file=@/path/to/book.pdf"

# Upload a TXT with male voice
curl -X POST http://localhost:5000/upload \
     -F "file=@/path/to/book.txt" \
     -F "voice_type=male"

# Stream audio (download to file for testing)
curl http://localhost:5000/audio/FILENAME.mp3 --output output.mp3

# Health check
curl http://localhost:5000/health
```

### Python (requests)

```python
import requests

# Upload
with open("book.pdf", "rb") as f:
    response = requests.post(
        "http://localhost:5000/upload",
        files={"file": f},
        data={"voice_type": "female"},
    )

data = response.json()
print(data["audio_url"])   # /audio/abc123.mp3

# Stream audio
audio_response = requests.get(f"http://localhost:5000{data['audio_url']}")
with open("output.mp3", "wb") as out:
    out.write(audio_response.content)
```

### JavaScript (fetch)

```javascript
const form = new FormData();
form.append("file", fileInput.files[0]);
form.append("voice_type", "female");

const response = await fetch("http://localhost:5000/upload", {
  method: "POST",
  body: form,
});

const { audio_url } = await response.json();
const audio = new Audio(audio_url);
audio.play();
```

---

## Voice Type Details

gTTS does not support true gender voices. We simulate gender by adjusting speed:

| `voice_type` | Speed  | Perceived effect         |
|-------------|--------|---------------------------|
| `female`    | Normal | Lighter, higher pitch     |
| `male`      | Slow   | Deeper, more deliberate   |

This is a deliberate architectural choice — `tts_engine.py` exposes a clean `generate_audio(text, voice_type)` interface, so replacing gTTS with ElevenLabs or OpenAI TTS requires changing only the `_generate_with_*` internal function.

---

## Future Roadmap

| Phase | Feature                                       |
|-------|-----------------------------------------------|
| 1     | ElevenLabs / OpenAI TTS for real AI voices   |
| 2     | User authentication (Flask-Login / JWT)       |
| 3     | MySQL / PostgreSQL database                   |
| 4     | Subscription plans (Stripe)                   |
| 5     | AWS S3 / GCS cloud storage                    |
| 6     | Background job queues (Celery + Redis)        |
| 7     | Chapter detection & chapter-based audio       |
| 8     | Chrome extension integration                  |
| 9     | OCR support for scanned PDFs                  |
| 10    | EPUB / MOBI format support                    |

---

## License

MIT — free to use, fork, and build upon.
