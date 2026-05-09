"""
utils/pdf_parser.py — Extracts plain text from PDF files using PyPDF2.

Designed to be swapped out for pdfplumber / pdfminer in the future
if richer extraction (tables, columns) is needed.
"""

import logging
from PyPDF2 import PdfReader
from PyPDF2.errors import PdfReadError

logger = logging.getLogger(__name__)


def extract_text_from_pdf(file_path: str) -> str:
    """
    Read a PDF file and return all page text concatenated.

    Args:
        file_path: Absolute path to the PDF on disk.

    Returns:
        Extracted text as a single string.

    Raises:
        ValueError: If the file is empty, encrypted, or yields no text.
        RuntimeError: If PyPDF2 cannot read the file at all.
    """
    try:
        reader = PdfReader(file_path)
    except PdfReadError as exc:
        logger.error("PyPDF2 failed to open '%s': %s", file_path, exc)
        raise RuntimeError(f"Could not parse PDF: {exc}") from exc
    except Exception as exc:
        logger.error("Unexpected error opening '%s': %s", file_path, exc)
        raise RuntimeError(f"Unexpected error reading PDF: {exc}") from exc

    # Reject encrypted PDFs early (password-protected).
    if reader.is_encrypted:
        raise ValueError("PDF is password-protected. Please provide an unlocked file.")

    if len(reader.pages) == 0:
        raise ValueError("PDF contains no pages.")

    pages_text: list[str] = []
    for page_number, page in enumerate(reader.pages, start=1):
        try:
            page_text = page.extract_text() or ""
            pages_text.append(page_text)
        except Exception as exc:
            # Log but continue — don't fail the whole book on one bad page.
            logger.warning("Could not extract text from page %d: %s", page_number, exc)

    full_text = "\n".join(pages_text).strip()

    if not full_text:
        raise ValueError(
            "No readable text found in the PDF. "
            "The file may be image-only (scanned). OCR support is on the roadmap."
        )

    logger.info("Extracted %d characters from %d pages.", len(full_text), len(reader.pages))
    return full_text
