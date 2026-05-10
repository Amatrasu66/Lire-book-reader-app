# Lire — AI Audiobook Reader

Lire transforms PDFs, EPUBs, and text documents into immersive AI-powered audiobook experiences with synchronized transcripts, dynamic playback controls, and a modern reading interface.

## Live Demo

https://lire-book-reader-app-frontend.onrender.com

---

# Features

## AI Audiobook Generation
- Upload PDF, EPUB, or TXT files
- Automatically converts documents into spoken audio
- Chunked TTS pipeline optimized for long-form reading

## Smart Reading Experience
- Real-time transcript synchronization
- Dynamic transcript highlighting
- Follow transcript mode
- Smooth audiobook-style playback interface

## Modern Player UI
- Interactive waveform visualization
- Playback controls
- Speed controls
- Forward/backward seeking
- Dark mode and light mode

## Dynamic Document Processing
- PDF first-page cover extraction
- Persistent session handling
- Upload drag-and-drop support
- Responsive design

## Optimized Backend
- Memory-optimized chunk processing
- Sequential TTS generation
- Render deployment compatible
- Large-document handling pipeline

---

# Tech Stack

## Frontend
- HTML
- TypeScript
- CSS
- Vite

## Backend
- Python
- Flask
- Edge-TTS
- PyMuPDF
- PyPDF2

## Deployment
- Render

---

# Project Structure

```bash
Lire/
├── backend/
│   ├── app.py
│   ├── upload_routes.py
│   ├── tts_engine.py
│   ├── pdf_parser.py
│   ├── config.py
│   ├── uploads/
│   ├── audio/
│   └── static/
│
├── frontend/
│   ├── src/
│   │   ├── js/
│   │   ├── css/
│   │   └── assets/
│   │
│   ├── index.html
│   ├── player.html
│   ├── package.json
│   └── vite.config.ts
│
└── README.md
```

---

# Installation

## Clone Repository

```bash
git clone https://github.com/Amatrasu66/Lire-book-reader-app.git
cd Lire-book-reader-app
```

---

# Backend Setup

## Navigate to backend

```bash
cd backend
```

## Create virtual environment

```bash
python -m venv venv
```

## Activate environment

### Windows

```bash
venv\Scripts\activate
```

### macOS/Linux

```bash
source venv/bin/activate
```

## Install dependencies

```bash
pip install -r requirements.txt
```

## Run backend

```bash
python app.py
```

Backend runs on:

```bash
http://127.0.0.1:5000
```

---

# Frontend Setup

## Navigate to frontend

```bash
cd frontend
```

## Install dependencies

```bash
npm install
```

## Run development server

```bash
npm run dev
```

Frontend runs on:

```bash
http://localhost:3000
```

---

# Deployment

## Backend
Deployed using Render Web Service.

## Frontend
Deployed using Render Static Site.

---

# Current Capabilities

- PDF narration
- EPUB narration
- Transcript synchronization
- Dynamic waveform playback
- Persistent reading sessions
- Cover extraction
- Theme switching
- Long-form chunked audiobook generation

---

# Future Improvements

- Real AI voice selection
- Multi-language support
- User authentication
- Cloud storage
- Bookmarking system
- Mobile app
- Advanced transcript alignment
- Streaming audio generation
- AI summaries

---

# Performance Notes

Lire uses:
- sequential chunk processing
- memory-optimized TTS generation
- low-RAM audiobook pipeline

to remain stable on free cloud hosting platforms.

---

# Author

Amatrasu66

GitHub:  
https://github.com/Amatrasu66

---

# License

This project is licensed under the MIT License.
