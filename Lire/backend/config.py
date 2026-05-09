"""
config.py — Central configuration for the Book Listener backend.
All environment-sensitive values live here. Swap for environment variables
when moving to production (e.g. os.getenv("MAX_CONTENT_LENGTH", 16 * 1024 * 1024)).
"""

import os

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR  = os.path.join(BASE_DIR, "uploads")
AUDIO_DIR   = os.path.join(BASE_DIR, "audio")
STATIC_DIR  = os.path.join(BASE_DIR, "static")

# ── Upload constraints ─────────────────────────────────────────────────────────
MAX_CONTENT_LENGTH = 32 * 1024 * 1024   # 32 MB hard limit enforced by Flask
ALLOWED_EXTENSIONS = {"pdf", "txt"}

# ── TTS settings ───────────────────────────────────────────────────────────────
# gTTS language code — extend this dict for multilingual support later.
TTS_LANGUAGE = "en"

# Voice-type → gTTS "slow" flag mapping.
# gTTS has no real gender voices; we use speed as a proxy and document this
# clearly so future engineers can swap in ElevenLabs / OpenAI TTS easily.
VOICE_CONFIGS = {
    "female": {"slow": False},   # default speed → higher-pitch perception
    "male":   {"slow": True},    # slightly slower → lower-pitch perception
}
DEFAULT_VOICE = "female"

# ── Cleanup ────────────────────────────────────────────────────────────────────
# Files older than this (seconds) are removed by the cleanup utility.
FILE_MAX_AGE_SECONDS = 60 * 60 * 2     # 2 hours

# ── Flask ──────────────────────────────────────────────────────────────────────
DEBUG = os.getenv("FLASK_DEBUG", "true").lower() == "true"
HOST  = os.getenv("FLASK_HOST", "0.0.0.0")
PORT  = int(os.getenv("FLASK_PORT", 5000))
