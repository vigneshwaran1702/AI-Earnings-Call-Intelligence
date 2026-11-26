"""LLM summarization engine (Gemini REST API + extractive fallback)."""

import json
import logging
import re
import httpx

from app.config import GEMINI_API_KEY
from app.summarization.chunking import chunk_text
from app.summarization.prompts import (
    SYSTEM_PROMPT,
    build_chunk_prompt,
    build_final_summary_prompt,
)

logger = logging.getLogger(__name__)

GEMINI_MODEL = "gemini-2.0-flash"
GEMINI_ENDPOINT = (
    f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"
)


def _call_gemini(prompt: str, json_mode: bool = False) -> str:
    """Call Gemini REST API via httpx."""
    payload: dict = {
        "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.2},
    }
    if json_mode:
        payload["generationConfig"]["responseMimeType"] = "application/json"

    with httpx.Client(timeout=60.0) as client:
        resp = client.post(
            GEMINI_ENDPOINT,
            params={"key": GEMINI_API_KEY},
            json=payload,
        )
        resp.raise_for_status()
        data = resp.json()

    candidates = data.get("candidates", [])
    if not candidates:
        raise ValueError("Gemini returned no candidates")
    parts = candidates[0].get("content", {}).get("parts", [])
    return "".join(p.get("text", "") for p in parts).strip()


def summary_to_markdown(summary: dict) -> str:
    """Render structured summary dict into clean Markdown."""
    lines = [
        f"# {summary.get('company', 'Company')} — {summary.get('quarter', '')} AI Earnings Summary",
        f"**Sentiment:** {summary.get('sentiment', 'Neutral')} | **Call Date:** {summary.get('call_date', '—')}\n",
    ]
    for sec in summary.get("sections", []):
        lines.append(f"## {sec.get('title', '')}")
        lines.append(sec.get("content", ""))
        for quote in sec.get("evidence", []):
            lines.append(f"> \"{quote}\"")
        lines.append("")
    return "\n".join(lines).strip()


def _extractive_fallback(company: str, quarter: str, call_date: str, text: str) -> dict:
    """Deterministic extractive fallback when GEMINI_API_KEY is not configured."""
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if len(p.strip()) > 40]
    sample_quotes = [p[:220].replace("\n", " ") for p in paragraphs[:4]]
    overview = paragraphs[0][:400] if paragraphs else "Transcript extracted successfully."

    section_titles = [
        "1. Executive Summary",
        "2. Financial Performance",
        "3. Segmental & Operational Drivers",
        "4. Management Guidance & Outlook",
        "5. Capital Allocation & Cash Flow",
        "6. Key Risks & Headwinds",
        "7. Analyst Q&A Takeaways",
    ]
    sections = []
    for i, title in enumerate(section_titles):
        content = paragraphs[i][:350] if i < len(paragraphs) else overview
        evidence = [sample_quotes[i % len(sample_quotes)]] if sample_quotes else []
        sections.append({"title": title, "content": content, "evidence": evidence})

    return {
        "company": company,
        "quarter": quarter or "Recent",
        "call_date": call_date or "",
        "executive_summary": overview,
        "sentiment": "Neutral",
        "management_guidance": "See extracted transcript for full management commentary.",
        "key_risks": ["Automated extractive summary (set GEMINI_API_KEY for full LLM analysis)."],
        "financial_highlights": [],
        "sections": sections,
    }


def summarize_transcript(
    text: str,
    company: str,
    quarter: str = "",
    call_date: str = "",
) -> tuple[dict, str]:
    """
    Summarize cleaned transcript text into (summary_dict, summary_markdown).
    Uses Gemini if GEMINI_API_KEY is configured, otherwise falls back cleanly.
    """
    if not text or not text.strip():
        raise ValueError("Cannot summarize empty transcript text")

    if not GEMINI_API_KEY:
        logger.info("GEMINI_API_KEY not set — using extractive fallback for %s", company)
        summary = _extractive_fallback(company, quarter, call_date, text)
        return summary, summary_to_markdown(summary)

    chunks = chunk_text(text)
    if len(chunks) == 1:
        combined_notes = chunks[0]
    else:
        notes: list[str] = []
        for idx, chunk in enumerate(chunks, start=1):
            prompt = build_chunk_prompt(company, quarter, chunk, idx, len(chunks))
            notes.append(_call_gemini(prompt, json_mode=False))
        combined_notes = "\n\n".join(notes)

    final_prompt = build_final_summary_prompt(company, quarter, call_date, combined_notes)
    raw_json = _call_gemini(final_prompt, json_mode=True)
    summary = json.loads(raw_json)
    return summary, summary_to_markdown(summary)
