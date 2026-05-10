"""
routes/upload_routes.py — All file-upload and audio-serving endpoints.

Endpoints
---------
  POST /upload          — Upload a PDF or TXT file, extract text, generate audio.
  GET  /audio/<filename> — Stream a generated MP3 file.
  POST /cleanup         — Manually trigger temp-file cleanup (admin use).
"""

import logging
import os
import uuid

from flask import Blueprint, jsonify, request, send_file
from werkzeug.utils import secure_filename

import config
from file_manager import (
    cleanup_all_temp_files,
    delete_file,
    get_file_extension,
    is_allowed_file,
    safe_audio_path,
)
from pdf_parser import extract_text_from_pdf
from tts_engine import generate_audio
from txt_parser import extract_text_from_txt

logger = logging.getLogger(__name__)

upload_bp = Blueprint("upload", __name__)


# ── POST /upload ───────────────────────────────────────────────────────────────

@upload_bp.route("/upload", methods=["POST"])
def upload_file():
    """
    Full pipeline: receive file → validate → save → extract text → TTS → MP3.

    Form fields:
        file       (required) — The PDF or TXT file.
        voice_type (optional) — "male" or "female" (default: "female").

    Returns 200 JSON on success, 4xx/5xx JSON on error.
    """

    # ── 1. Validate file presence ──────────────────────────────────────────────
    if "file" not in request.files:
        return _error("No file field in the request.", 400)

    uploaded_file = request.files["file"]

    if uploaded_file.filename == "":
        return _error("No file selected.", 400)

    original_name = uploaded_file.filename

    if not is_allowed_file(original_name):
        return _error(
            f"File type not allowed. Accepted types: {', '.join(config.ALLOWED_EXTENSIONS)}",
            415,
        )

    # ── 2. Save uploaded file ──────────────────────────────────────────────────
    safe_name = secure_filename(original_name)
    file_id   = uuid.uuid4().hex
    extension = get_file_extension(safe_name)
    stored_name = f"{file_id}.{extension}"
    upload_path = os.path.join(config.UPLOAD_DIR, stored_name)

    try:
        uploaded_file.save(upload_path)
        logger.info("Saved upload: %s → %s", original_name, upload_path)
    except OSError as exc:
        logger.error("Could not save uploaded file: %s", exc)
        return _error("Could not save the uploaded file. Please try again.", 500)

    # ── 3. Extract text ────────────────────────────────────────────────────────
    try:
        if extension == "pdf":
            parsed = extract_text_from_pdf(upload_path)
            text = parsed["text"]
            cover_filename = parsed["cover"]
        else:
            text = extract_text_from_txt(upload_path)
            cover_filename = None
    except ValueError as exc:
        delete_file(upload_path)
        return _error(str(exc), 422)
    except RuntimeError as exc:
        delete_file(upload_path)
        return _error(str(exc), 500)

    # ── 4. Convert text to speech ──────────────────────────────────────────────
    voice_type = request.form.get("voice_type", config.DEFAULT_VOICE).lower().strip()

    try:
        audio_filename = generate_audio(text, voice_type)
    except ValueError as exc:
        delete_file(upload_path)
        return _error(str(exc), 400)
    except RuntimeError as exc:
        delete_file(upload_path)
        return _error(str(exc), 500)

    # ── 5. Clean up the uploaded source file (we don't need it anymore) ────────
    delete_file(upload_path)

    # ── 6. Return success ──────────────────────────────────────────────────────
    audio_url = f"/audio/{audio_filename}"
    logger.info("Pipeline complete. Audio URL: %s", audio_url)

    return jsonify(
    {
        "success": True,

        "audio_url": f"/audio/{audio_filename}",

        "text": text,

        "title": original_name.rsplit(".", 1)[0],

        "cover_image":
            f"http://127.0.0.1:5000/static/{cover_filename}"
            if cover_filename
            else None,

        "file_id": file_id,

        "message": "Document processed successfully"
    }
), 200


# ── GET /audio/<filename> ──────────────────────────────────────────────────────

@upload_bp.route("/audio/<filename>", methods=["GET"])
def serve_audio(filename: str):
    """
    Stream a generated MP3 file to the client.

    Path traversal is blocked by safe_audio_path().
    The browser can use the <audio> element with this URL directly.
    """
    resolved = safe_audio_path(filename)

    if resolved is None:
        return _error("Invalid file path.", 400)

    if not os.path.exists(resolved):
        return _error("Audio file not found.", 404)

    return send_file(
        resolved,
        mimetype="audio/mpeg",
        as_attachment=False,   # Stream inline (browser plays it directly).
        download_name=filename,
        conditional=True,      # Support HTTP Range requests for seeking.
    )


# ── POST /cleanup ──────────────────────────────────────────────────────────────

@upload_bp.route("/cleanup", methods=["POST"])
def cleanup():
    """
    Manually trigger cleanup of old upload and audio files.
    In production, secure this endpoint behind admin authentication.
    """
    result = cleanup_all_temp_files()
    return jsonify(
        {
            "success": True,
            "removed": result,
            "message": "Cleanup completed.",
        }
    ), 200


# ── GET /health ────────────────────────────────────────────────────────────────

@upload_bp.route("/health", methods=["GET"])
def health():
    """Simple liveness probe — useful for Docker / load-balancer health checks."""
    return jsonify({"status": "ok", "service": "book-listener-api"}), 200


# ── Internal helpers ───────────────────────────────────────────────────────────

def _error(message: str, status_code: int):
    """Return a standard JSON error response."""
    logger.warning("Returning %d: %s", status_code, message)
    return jsonify({"success": False, "error": message}), status_code
