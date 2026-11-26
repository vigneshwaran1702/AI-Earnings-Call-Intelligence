"""
PDF Downloader

Downloads transcript PDFs from exchange attachment URLs.
Handles retries, file validation, safe filenames, and
rejects unknown domains for security.
"""

import logging
import re
from pathlib import Path
from urllib.parse import urlparse
import requests

from app.config import TRANSCRIPT_DIR

logger = logging.getLogger(__name__)

ALLOWED_HOSTS = {
    "nsearchives.nseindia.com",
    "www.nseindia.com",
    "archives.nseindia.com",
    "www.bseindia.com",
    "api.bseindia.com",
    "bseindia.com",
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 Chrome/140.0.0.0 Safari/537.36"
    ),
}

MAX_RETRIES = 3
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB


def safe_filename(value: str) -> str:
    """Sanitize a string for use as a filename."""
    value = re.sub(r"[^a-zA-Z0-9_\-.]", "_", value)
    return value[:100] or "transcript"


def download_pdf(url: str, filing_id: str) -> str | None:
    """
    Download a PDF from the given URL and save it to TRANSCRIPT_DIR.

    Returns the saved file path on success, or None on failure.
    Intentionally rejects unknown domains and non-PDF responses.
    """
    if not url:
        logger.warning("No attachment URL for %s", filing_id)
        return None

    # ── Validate URL host ──────────────────────────────────────────
    parsed = urlparse(url)
    hostname = parsed.hostname or ""

    if hostname not in ALLOWED_HOSTS:
        logger.warning(
            "Blocked download from unknown host '%s' for %s",
            hostname, filing_id,
        )
        return None

    # ── Check if already downloaded ────────────────────────────────
    filename = safe_filename(filing_id) + ".pdf"
    filepath = TRANSCRIPT_DIR / filename

    if filepath.exists() and filepath.stat().st_size > 1000:
        logger.info("Already downloaded: %s", filepath.name)
        return str(filepath)

    # ── Download with retries ──────────────────────────────────────
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logger.info(
                "Downloading %s (attempt %d/%d)",
                url[:80], attempt, MAX_RETRIES,
            )

            response = requests.get(
                url,
                headers=HEADERS,
                timeout=60,
                stream=True,
            )
            response.raise_for_status()

            # ── Validate content type ──────────────────────────────
            content_type = response.headers.get("Content-Type", "").lower()
            if "pdf" not in content_type and "octet-stream" not in content_type:
                logger.warning(
                    "Non-PDF content type '%s' for %s — skipping",
                    content_type, filing_id,
                )
                return None

            # ── Check file size ────────────────────────────────────
            content_length = response.headers.get("Content-Length")
            if content_length and int(content_length) > MAX_FILE_SIZE:
                logger.warning(
                    "File too large (%s bytes) for %s — skipping",
                    content_length, filing_id,
                )
                return None

            # ── Stream to disk ─────────────────────────────────────
            TRANSCRIPT_DIR.mkdir(parents=True, exist_ok=True)
            total_bytes = 0

            with open(filepath, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    total_bytes += len(chunk)
                    if total_bytes > MAX_FILE_SIZE:
                        logger.warning("Download exceeded size limit for %s", filing_id)
                        filepath.unlink(missing_ok=True)
                        return None
                    f.write(chunk)

            # ── Validate PDF header ────────────────────────────────
            with open(filepath, "rb") as f:
                header = f.read(5)

            if header != b"%PDF-":
                logger.warning(
                    "Downloaded file is not a valid PDF for %s — removing",
                    filing_id,
                )
                filepath.unlink(missing_ok=True)
                return None

            logger.info(
                "Saved %s (%d KB)",
                filepath.name, total_bytes // 1024,
            )
            return str(filepath)

        except requests.exceptions.RequestException as exc:
            logger.warning(
                "Download attempt %d failed for %s: %s",
                attempt, filing_id, exc,
            )
            if attempt == MAX_RETRIES:
                logger.error("All download attempts failed for %s", filing_id)
                return None

    return None


def download_all(items: list[dict]) -> dict[str, str]:
    """
    Download PDFs for a list of announcement items.
    Returns a dict mapping filing_id → local file path.
    """
    downloaded: dict[str, str] = {}

    for item in items:
        url = item.get("source_url", "")
        filing_id = item.get("filing_id", "unknown")

        # Only attempt if URL looks like a PDF
        url_lower = url.lower().split("?")[0]
        if not url_lower.endswith(".pdf"):
            logger.debug(
                "Skipping non-PDF URL for %s: %s",
                filing_id, url[:60],
            )
            continue

        result = download_pdf(url, filing_id)
        if result:
            downloaded[filing_id] = result

    logger.info(
        "Downloaded %d PDFs out of %d items",
        len(downloaded), len(items),
    )
    return downloaded

