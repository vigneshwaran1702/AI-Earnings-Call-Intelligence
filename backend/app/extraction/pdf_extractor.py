"""PDF text extraction using PyMuPDF with OCR fallback."""

import logging
from pathlib import Path
import pymupdf

from app.extraction.ocr import extract_text_with_ocr
from app.extraction.text_cleaner import clean_transcript_text

logger = logging.getLogger(__name__)


def extract_text_from_pdf(pdf_path: str | Path, min_chars_per_page: int = 80) -> str:
    """Extract raw text from a PDF; fall back to OCR if pages appear scanned."""
    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {path}")

    doc = pymupdf.open(str(path))
    pages_text: list[str] = []
    try:
        for page in doc:
            pages_text.append(page.get_text("text") or "")
        page_count = len(doc)
    finally:
        doc.close()

    combined = "\n".join(pages_text).strip()
    if page_count > 0 and len(combined) < page_count * min_chars_per_page:
        logger.info("Low text density in %s — attempting OCR fallback", path.name)
        ocr_text = extract_text_with_ocr(path)
        if len(ocr_text.strip()) > len(combined):
            combined = ocr_text

    return combined


def extract_and_clean_pdf(pdf_path: str | Path) -> str:
    """Extract text from PDF and normalize/clean it for LLM summarization."""
    raw = extract_text_from_pdf(pdf_path)
    return clean_transcript_text(raw)
