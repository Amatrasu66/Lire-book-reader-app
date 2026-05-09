"""
utils/file_manager.py — Filesystem helpers for uploads and audio files.

Responsibilities:
  - Validate file extensions.
  - Ensure storage directories exist.
  - Delete old / temporary files.
  - Provide safe path resolution (guards against path traversal).
"""

import logging
import os
import time

import config

logger = logging.getLogger(__name__)


# ── Directory bootstrap ────────────────────────────────────────────────────────

def ensure_directories() -> None:
    """
    Create upload and audio directories if they don't already exist.
    Call once at application startup.
    """
    for directory in (config.UPLOAD_DIR, config.AUDIO_DIR, config.STATIC_DIR):
        os.makedirs(directory, exist_ok=True)
        logger.debug("Directory ready: %s", directory)


# ── Validation ─────────────────────────────────────────────────────────────────

def is_allowed_file(filename: str) -> bool:
    """
    Return True if the filename has an extension in ALLOWED_EXTENSIONS.

    Args:
        filename: Original filename from the HTTP upload (not yet sanitised).
    """
    if "." not in filename:
        return False
    extension = filename.rsplit(".", 1)[1].lower()
    return extension in config.ALLOWED_EXTENSIONS


def get_file_extension(filename: str) -> str:
    """
    Return the lowercase extension of filename (without the dot).

    Assumes is_allowed_file() has already been called.
    """
    return filename.rsplit(".", 1)[1].lower()


# ── Safe path resolution ───────────────────────────────────────────────────────

def safe_audio_path(filename: str) -> str | None:
    """
    Resolve an audio filename to its absolute path, guarding against
    path traversal attacks (e.g. '../../etc/passwd').

    Args:
        filename: The bare filename requested by the client.

    Returns:
        Absolute path string if the file is inside AUDIO_DIR, else None.
    """
    audio_dir_real = os.path.realpath(config.AUDIO_DIR)
    requested_path = os.path.realpath(os.path.join(config.AUDIO_DIR, filename))

    # Ensure the resolved path is still inside the audio directory.
    if not requested_path.startswith(audio_dir_real + os.sep):
        logger.warning("Path traversal attempt blocked: '%s'", filename)
        return None

    return requested_path


# ── Cleanup ────────────────────────────────────────────────────────────────────

def delete_file(file_path: str) -> bool:
    """
    Delete a single file. Returns True on success, False if not found.
    """
    if not os.path.exists(file_path):
        return False
    try:
        os.remove(file_path)
        logger.debug("Deleted: %s", file_path)
        return True
    except OSError as exc:
        logger.error("Could not delete '%s': %s", file_path, exc)
        return False


def cleanup_old_files(directory: str, max_age_seconds: int = config.FILE_MAX_AGE_SECONDS) -> int:
    """
    Remove files in `directory` that are older than `max_age_seconds`.

    Args:
        directory:       Path to the directory to scan.
        max_age_seconds: Files older than this are deleted.

    Returns:
        Number of files successfully deleted.
    """
    if not os.path.isdir(directory):
        logger.warning("Cleanup skipped — directory not found: %s", directory)
        return 0

    cutoff = time.time() - max_age_seconds
    deleted_count = 0

    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if not os.path.isfile(file_path):
            continue
        try:
            mtime = os.path.getmtime(file_path)
            if mtime < cutoff:
                os.remove(file_path)
                deleted_count += 1
                logger.debug("Cleaned up old file: %s", file_path)
        except OSError as exc:
            logger.warning("Could not inspect/delete '%s': %s", file_path, exc)

    logger.info("Cleanup of '%s': removed %d old file(s).", directory, deleted_count)
    return deleted_count


def cleanup_all_temp_files() -> dict:
    """
    Run cleanup on both uploads and audio directories.
    Intended to be called on a schedule (cron / APScheduler in the future).

    Returns:
        Dict with counts of files removed per directory.
    """
    return {
        "uploads_deleted": cleanup_old_files(config.UPLOAD_DIR),
        "audio_deleted":   cleanup_old_files(config.AUDIO_DIR),
    }
