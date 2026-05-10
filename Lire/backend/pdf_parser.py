import logging
import os
import uuid

import fitz

from PyPDF2 import PdfReader
from PyPDF2.errors import PdfReadError

import config

logger = logging.getLogger(__name__)


def extract_text_from_pdf(file_path: str):

    try:

        reader = PdfReader(file_path)

    except PdfReadError as exc:

        raise RuntimeError(
            f"Could not parse PDF: {exc}"
        )

    if reader.is_encrypted:

        raise ValueError(
            "PDF is password protected"
        )

    pages_text = []

    for page in reader.pages:

        try:

            text = page.extract_text() or ""

            pages_text.append(text)

        except Exception:

            pass

    full_text = "\n".join(pages_text).strip()

    if not full_text:

        raise ValueError(
            "No readable text found"
        )

    cover_filename = extract_cover(file_path)

    return {

        "text": full_text,

        "cover": cover_filename
    }


def extract_cover(pdf_path: str):

    try:
        doc = fitz.open(pdf_path)
        page = doc.load_page(0)
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        
        cover_filename = f"{uuid.uuid4().hex}.png"
        output_path = os.path.join(config.STATIC_DIR, cover_filename)
        pix.save(output_path)
        
        # Explicitly close handle to liberate loaded binary resources immediately
        doc.close()
        
        return cover_filename

    except Exception as exc:

        logger.warning(
            "Could not generate cover: %s",
            exc
        )

    return None