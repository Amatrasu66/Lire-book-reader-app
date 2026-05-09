"""
utils/tts_engine.py — Text-to-Speech abstraction layer.

ARCHITECTURE NOTE
-----------------
This module intentionally wraps gTTS behind a clean interface so future
engineers can swap in ElevenLabs, OpenAI TTS, or any other engine by only
editing this file. The rest of the codebase calls `generate_audio()` and
never touches gTTS directly.

gTTS gender limitation
-----------------------
gTTS does not support true gender voices. We simulate selection by:
  - "female" → normal speed (gTTS default, perceived as lighter/higher)
  - "male"   → slow=True  (perceived as deeper/more deliberate)

When you integrate ElevenLabs or OpenAI TTS, replace _generate_with_gtts()
with _generate_with_elevenlabs() and update VOICE_CONFIGS in config.py.
"""

import logging
import os
import uuid

from gtts import gTTS
from gtts.tts import gTTSError

import config

logger = logging.getLogger(__name__)

# ── gTTS character limit (practical) ──────────────────────────────────────────
# gTTS can hit Google's API limit on very long texts. We chunk large texts.
_CHUNK_SIZE = 5_000   # characters per chunk


def generate_audio(text: str, voice_type: str = config.DEFAULT_VOICE) -> str:
    """
    Convert text to speech and save the result as an MP3 file.

    Args:
        text:       The text to synthesise.
        voice_type: "male" or "female" (see module docstring for details).

    Returns:
        The filename (not full path) of the generated MP3, e.g. "abc123.mp3".
        Callers can build the full path with config.AUDIO_DIR / filename.

    Raises:
        ValueError: If voice_type is unrecognised or text is empty.
        RuntimeError: If the TTS engine or filesystem operation fails.
    """
    text = text.strip()
    if not text:
        raise ValueError("Cannot generate audio from empty text.")

    voice_type = voice_type.lower().strip()
    if voice_type not in config.VOICE_CONFIGS:
        raise ValueError(
            f"Unknown voice type '{voice_type}'. "
            f"Valid options: {list(config.VOICE_CONFIGS.keys())}"
        )

    audio_filename = f"{uuid.uuid4().hex}.mp3"
    audio_path = os.path.join(config.AUDIO_DIR, audio_filename)

    try:
        _generate_with_gtts(text, voice_type, audio_path)
    except RuntimeError:
        raise
    except Exception as exc:
        logger.error("Unexpected TTS failure: %s", exc)
        raise RuntimeError(f"Audio generation failed unexpectedly: {exc}") from exc

    logger.info("Audio saved → %s (%d bytes)", audio_path, os.path.getsize(audio_path))
    return audio_filename


# ── Engine implementations ─────────────────────────────────────────────────────

def _generate_with_gtts(text: str, voice_type: str, output_path: str) -> None:
    """
    Internal: synthesise audio using gTTS.

    Chunks long texts to avoid hitting Google's silent character limit.
    Saves a single concatenated MP3 to output_path.
    """
    voice_cfg = config.VOICE_CONFIGS[voice_type]
    chunks = _split_text(text, _CHUNK_SIZE)

    logger.info(
        "gTTS: synthesising %d chunk(s) | lang=%s | slow=%s",
        len(chunks), config.TTS_LANGUAGE, voice_cfg["slow"],
    )

    if len(chunks) == 1:
        # Fast path — single chunk, write directly.
        _gtts_write(chunks[0], voice_cfg, output_path)
    else:
        # Multi-chunk: write each to a temp file, then concatenate.
        _gtts_write_chunks(chunks, voice_cfg, output_path)


def _gtts_write(text: str, voice_cfg: dict, output_path: str) -> None:
    """Synthesise a single text chunk and write to output_path."""
    try:
        tts = gTTS(text=text, lang=config.TTS_LANGUAGE, slow=voice_cfg["slow"])
        tts.save(output_path)
    except gTTSError as exc:
        logger.error("gTTS API error: %s", exc)
        raise RuntimeError(f"TTS service error: {exc}") from exc
    except OSError as exc:
        logger.error("Could not write audio file '%s': %s", output_path, exc)
        raise RuntimeError(f"Could not save audio file: {exc}") from exc


def _gtts_write_chunks(chunks: list[str], voice_cfg: dict, output_path: str) -> None:
    """
    Synthesise multiple text chunks and concatenate into one MP3.

    MP3 files can be binary-concatenated — the decoder handles frame
    boundaries correctly, so this is safe without re-encoding.
    """
    chunk_paths: list[str] = []
    base_name = output_path.replace(".mp3", "")

    try:
        for index, chunk in enumerate(chunks):
            chunk_path = f"{base_name}_part{index}.mp3"
            _gtts_write(chunk, voice_cfg, chunk_path)
            chunk_paths.append(chunk_path)

        # Concatenate all chunk files into the final output.
        with open(output_path, "wb") as out_file:
            for chunk_path in chunk_paths:
                with open(chunk_path, "rb") as chunk_file:
                    out_file.write(chunk_file.read())

    finally:
        # Always clean up partial chunk files.
        for chunk_path in chunk_paths:
            if os.path.exists(chunk_path):
                try:
                    os.remove(chunk_path)
                except OSError:
                    pass   # Non-fatal; leftover temp files are acceptable.


# ── Helpers ────────────────────────────────────────────────────────────────────

def _split_text(text: str, chunk_size: int) -> list[str]:
    """
    Split text into chunks of at most chunk_size characters,
    breaking at sentence boundaries ('. ') when possible.
    """
    if len(text) <= chunk_size:
        return [text]

    chunks: list[str] = []
    while len(text) > chunk_size:
        # Find the last sentence boundary within the chunk window.
        split_at = text.rfind(". ", 0, chunk_size)
        if split_at == -1:
            # No sentence boundary found; hard-split at chunk_size.
            split_at = chunk_size
        else:
            split_at += 1   # Include the period.

        chunks.append(text[:split_at].strip())
        text = text[split_at:].strip()

    if text:
        chunks.append(text)

    return chunks
