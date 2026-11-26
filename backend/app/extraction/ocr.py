"""Optional OCR fallback for scanned image-only PDFs."""

import logging
from pathlib import Path
import pymupdf

logger = logging.getLogger(__name__)


def extract_text_with_ocr(pdf_path: str | Path, dpi: int = 200) -> str:
    """
    Render PDF pages to images and run Tesseract OCR if available.
    Returns empty string gracefully if pytesseract/Pillow are not installed.
    """
    try:
        import pytesseract
        from PIL import Image
    except ImportError:
        logger.debug("pytesseract/Pillow not installed; skipping OCR for %s", pdf_path)
        return ""

    doc = pymupdf.open(str(pdf_path))
    texts: list[str] = []
    try:
        for idx, page in enumerate(doc):
            pix = page.get_pixmap(dpi=dpi)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            texts.append(pytesseract.image_to_string(img))
            logger.debug("OCR completed page %d/%d", idx + 1, len(doc))
    except Exception as exc:
        logger.warning("OCR failed for %s: %s", pdf_path, exc)
    finally:
        doc.close()

    return "\n".join(texts).strip()
