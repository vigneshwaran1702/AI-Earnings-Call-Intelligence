import json
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.transcript import Transcript
from app.config import TRACKED_COMPANIES

router = APIRouter(prefix="/api", tags=["Earnings Intelligence"])


# ── Companies ──────────────────────────────────────────────────────
@router.get("/companies")
def get_companies():
    """Return the list of tracked Indian companies."""
    return {
        "count": len(TRACKED_COMPANIES),
        "companies": TRACKED_COMPANIES,
    }


# ── Transcripts ────────────────────────────────────────────────────
@router.get("/transcripts")
def get_transcripts(
    company: str | None = None,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """List ingested transcripts, optionally filtered by company symbol."""
    query = db.query(Transcript).order_by(Transcript.id.desc())
    if company:
        query = query.filter(Transcript.symbol == company.upper())
    records = query.limit(limit).all()
    return [record.to_dict() for record in records]


@router.get("/transcripts/{transcript_id}")
def get_transcript(transcript_id: int, db: Session = Depends(get_db)):
    """Get full detail for a single transcript, including summary."""
    record = db.query(Transcript).filter(Transcript.id == transcript_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Transcript not found")
    data = record.to_dict()
    # Attach the full summary if available
    if record.summary_json:
        try:
            data["summary"] = json.loads(record.summary_json)
        except json.JSONDecodeError:
            data["summary"] = None
    if record.summary_markdown:
        data["summary_markdown"] = record.summary_markdown
    data["raw_text"] = record.raw_text
    data["pdf_download_url"] = f"/api/transcripts/{record.id}/pdf"
    return data


@router.get("/transcripts/{transcript_id}/pdf")
def download_transcript_pdf(transcript_id: int, db: Session = Depends(get_db)):
    """Download the transcript PDF file."""
    record = db.query(Transcript).filter(Transcript.id == transcript_id).first()
    if not record or not record.pdf_path:
        raise HTTPException(status_code=404, detail="PDF not found for this transcript")
    pdf_file = Path(record.pdf_path)
    if not pdf_file.exists():
        raise HTTPException(status_code=404, detail="PDF file missing on disk")
    return FileResponse(
        path=str(pdf_file),
        media_type="application/pdf",
        filename=pdf_file.name,
    )


# ── Dashboard stats ────────────────────────────────────────────────
@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    """Aggregate statistics for the dashboard overview cards."""
    total       = db.query(func.count(Transcript.id)).scalar() or 0
    processed   = db.query(func.count(Transcript.id)).filter(Transcript.processed == True).scalar() or 0  # noqa: E712
    companies   = db.query(func.count(func.distinct(Transcript.symbol))).scalar() or 0

    return {
        "tracked_companies":    len(TRACKED_COMPANIES),
        "total_transcripts":    total,
        "processed_summaries":  processed,
        "pending":              total - processed,
        "unique_companies":     companies,
        "pipeline_status":      "ready",
    }


# ── Health ─────────────────────────────────────────────────────────
@router.get("/health")
def health():
    return {"status": "healthy", "service": "Finosauras Intelligence"}

