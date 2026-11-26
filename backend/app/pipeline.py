"""
Automated Earnings-Call Pipeline

1. Collects concall announcements from NSE & BSE.
2. Deduplicates against SQLite by filing_id.
3. Downloads PDF attachments.
4. Extracts & cleans transcript text.
5. Summarizes into 7-section JSON + Markdown.
6. Saves results to SQLite & data/summaries/ and emits WebSocket events.
"""

import asyncio
import json
import logging
from pathlib import Path

from app.config import SUMMARY_DIR, TRACKED_COMPANIES
from app.database import SessionLocal
from app.models.transcript import Transcript
from app.ingestion.watcher import collect_concall_announcements
from app.ingestion.downloader import download_pdf
from app.extraction.pdf_extractor import extract_and_clean_pdf
from app.summarization.llm import summarize_transcript
from app.api.websocket import emit_event

logger = logging.getLogger(__name__)

TRACKED_SYMBOLS = {c["symbol"].upper() for c in TRACKED_COMPANIES}


def _process_single_filing(item: dict) -> dict | None:
    """Synchronous worker for one filing: download -> extract -> summarize -> save."""
    filing_id = item["filing_id"]
    url = item.get("source_url", "")

    db = SessionLocal()
    try:
        if db.query(Transcript).filter(Transcript.filing_id == filing_id).first():
            return None

        pdf_path = None
        raw_text = ""
        summary_json_str = None
        summary_md = None
        processed = False

        if url and url.lower().split("?")[0].endswith(".pdf"):
            pdf_path = download_pdf(url, filing_id)

        if pdf_path and Path(pdf_path).exists():
            raw_text = extract_and_clean_pdf(pdf_path)
            if raw_text:
                summary_dict, summary_md = summarize_transcript(
                    text=raw_text,
                    company=item["company"],
                    quarter=item.get("quarter", ""),
                    call_date=item.get("call_date", ""),
                )
                summary_json_str = json.dumps(summary_dict)
                (SUMMARY_DIR / f"{filing_id}.md").write_text(summary_md, encoding="utf-8")
                processed = True

        record = Transcript(
            company=item["company"],
            symbol=item.get("symbol") or None,
            exchange=item["exchange"],
            filing_id=filing_id,
            quarter=item.get("quarter") or None,
            call_date=item.get("call_date") or None,
            title=item.get("title") or None,
            source_url=url or None,
            pdf_path=pdf_path,
            raw_text=raw_text or None,
            summary_json=summary_json_str,
            summary_markdown=summary_md,
            processed=processed,
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record.to_dict()
    except Exception as exc:
        db.rollback()
        logger.error("Failed processing filing %s: %s", filing_id, exc)
        return None
    finally:
        db.close()


async def run_pipeline(max_items: int = 10, tracked_only: bool = False) -> dict:
    """Run one full ingestion -> extraction -> summarization cycle."""
    await emit_event("pipeline_started", {"message": "Scanning NSE & BSE for new concall filings..."})

    announcements = await asyncio.to_thread(collect_concall_announcements)
    if tracked_only:
        announcements = [
            a for a in announcements if (a.get("symbol") or "").upper() in TRACKED_SYMBOLS
        ]

    # Prioritize filings with PDF URLs
    pdf_first = sorted(
        announcements,
        key=lambda a: 0 if (a.get("source_url") or "").lower().split("?")[0].endswith(".pdf") else 1,
    )

    new_records: list[dict] = []
    for item in pdf_first[:max_items]:
        saved = await asyncio.to_thread(_process_single_filing, item)
        if saved:
            new_records.append(saved)
            await emit_event(
                "transcript_processed" if saved["processed"] else "filing_detected",
                {
                    "message": f"{saved['company']} ({saved['exchange']}): {saved.get('title', '')[:80]}",
                    "transcript": saved,
                },
            )

    summary = {
        "scanned": len(announcements),
        "processed_new": len(new_records),
    }
    await emit_event(
        "pipeline_completed",
        {"message": f"Scan complete: {len(announcements)} candidates, {len(new_records)} new saved.", **summary},
    )
    return summary
