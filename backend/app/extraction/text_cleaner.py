"""Transcript text cleaning and normalization."""

import re


_PAGE_NUM_RE = re.compile(r"(?im)^\s*(?:page\s+\d+(?:\s+of\s+\d+)?|\d+\s*/\s*\d+)\s*$")
_MULTI_NEWLINE_RE = re.compile(r"\n{3,}")
_MULTI_SPACE_RE = re.compile(r"[ \t]{2,}")


def clean_transcript_text(text: str) -> str:
    """Remove page numbers, normalize line breaks/spaces, and strip noise."""
    if not text:
        return ""

    cleaned = text.replace("\r\n", "\n").replace("\r", "\n").replace("\xa0", " ")
    lines = [line.strip() for line in cleaned.split("\n")]
    filtered = [line for line in lines if not _PAGE_NUM_RE.match(line)]

    cleaned = "\n".join(filtered)
    cleaned = _MULTI_SPACE_RE.sub(" ", cleaned)
    cleaned = _MULTI_NEWLINE_RE.sub("\n\n", cleaned)
    return cleaned.strip()
