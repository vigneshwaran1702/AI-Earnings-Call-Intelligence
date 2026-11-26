"""Long-document chunking for earnings call transcripts."""


def chunk_text(
    text: str,
    max_chars: int = 12000,
    overlap: int = 800,
) -> list[str]:
    """Split transcript text into overlapping chunks at paragraph/sentence boundaries."""
    if not text:
        return []
    if len(text) <= max_chars:
        return [text]

    chunks: list[str] = []
    start = 0
    length = len(text)

    while start < length:
        end = min(start + max_chars, length)
        if end < length:
            # Prefer splitting on paragraph or sentence boundary
            split_at = text.rfind("\n\n", start + max_chars // 2, end)
            if split_at == -1:
                split_at = text.rfind(". ", start + max_chars // 2, end)
            if split_at != -1:
                end = split_at + 1

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        if end >= length:
            break
        start = max(end - overlap, start + 1)

    return chunks
