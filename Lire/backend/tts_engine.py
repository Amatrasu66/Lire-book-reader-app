import logging
import os
import uuid

import pyttsx3

import config

logger = logging.getLogger(__name__)

engine = pyttsx3.init()

engine.setProperty("rate", 170)

engine.setProperty("volume", 1.0)

voices = engine.getProperty("voices")

MAX_CHARS_PER_CHUNK = 4500


def chunk_text(text, size=MAX_CHARS_PER_CHUNK):

    chunks = []

    for i in range(0, len(text), size):

        chunks.append(text[i:i + size])

    return chunks


def generate_audio(text: str, voice_type="female"):

    text = text.strip()

    if not text:

        raise ValueError("Empty text")

    audio_filename = f"{uuid.uuid4().hex}.mp3"

    output_path = os.path.join(
        config.AUDIO_DIR,
        audio_filename
    )

    if voices:

        if voice_type == "female" and len(voices) > 1:

            engine.setProperty(
                "voice",
                voices[1].id
            )

        else:

            engine.setProperty(
                "voice",
                voices[0].id
            )

    chunks = chunk_text(text)

    final_text = "\n".join(chunks)

    engine.save_to_file(
        final_text,
        output_path
    )

    engine.runAndWait()

    if not os.path.exists(output_path):

        raise RuntimeError(
            "Audio generation failed"
        )

    logger.info(
        "Generated audio: %s",
        output_path
    )

    return audio_filename