"""
utils/txt_parser.py — Reads plain-text (.txt) files safely.

Tries UTF-8 first, falls back to latin-1 to handle the widest range
of plain-text files a user might upload.
"""

import logging

logger = logging.getLogger(__name__)

# Byte-order marks to strip from the beginning of files.
_BOMS = [
    b"\xef\xbb\xbf",   # UTF-8 BOM
    b"\xff\xfe",        # UTF-16 LE BOM
    b"\xfe\xff",        # UTF-16 BE BOM
]


def extract_text_from_txt(file_path: str) -> str:
    """
    Read a plain-text file and return its contents as a string.

    Args:
        file_path: Absolute path to the .txt file on disk.

    Returns:
        File contents as a single string.

    Raises:
        ValueError: If the file is empty after stripping whitespace.
        RuntimeError: If the file cannot be opened or decoded.
    """
    # Try UTF-8 first; fall back to latin-1 which never raises a decode error.
    for encoding in ("utf-8", "latin-1"):
        try:
            with open(file_path, "rb") as raw_file:
                raw_bytes = raw_file.read()

            # Strip BOM if present.
            for bom in _BOMS:
                if raw_bytes.startswith(bom):
                    raw_bytes = raw_bytes[len(bom):]
                    break

            text = raw_bytes.decode(encoding)
            text = text.strip()

            if not text:
                raise ValueError("The uploaded text file is empty.")

            logger.info(
                "Read %d characters from TXT file using %s encoding.",
                len(text), encoding,
            )
            return text

        except (UnicodeDecodeError, LookupError):
            # Try next encoding.
            continue
        except ValueError:
            raise
        except OSError as exc:
            logger.error("Could not open '%s': %s", file_path, exc)
            raise RuntimeError(f"Could not read text file: {exc}") from exc

    # Both encodings failed.
    raise RuntimeError(
        "Could not decode the text file. "
        "Please ensure the file is UTF-8 or latin-1 encoded."
    )
