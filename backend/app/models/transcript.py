from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean,
)
from sqlalchemy.sql import func
from app.database import Base


class Transcript(Base):
    __tablename__ = "transcripts"

    id              = Column(Integer, primary_key=True, index=True)
    company         = Column(String(150), nullable=False, index=True)
    symbol          = Column(String(30), index=True)
    exchange        = Column(String(10), nullable=False)          # NSE | BSE
    filing_id       = Column(String(200), unique=True, index=True)
    quarter         = Column(String(30))                           # e.g. Q3 FY25
    call_date       = Column(String(30))
    title           = Column(String(500))
    source_url      = Column(Text)
    pdf_path        = Column(Text)
    raw_text        = Column(Text)
    summary_json    = Column(Text)
    summary_markdown = Column(Text)
    processed       = Column(Boolean, default=False)
    created_at      = Column(
        DateTime(timezone=True), server_default=func.now(),
    )

    def to_dict(self):
        return {
            "id":               self.id,
            "company":          self.company,
            "symbol":           self.symbol,
            "exchange":         self.exchange,
            "filing_id":        self.filing_id,
            "quarter":          self.quarter,
            "call_date":        self.call_date,
            "title":            self.title,
            "source_url":       self.source_url,
            "pdf_path":         self.pdf_path,
            "processed":        self.processed,
            "has_summary":      self.summary_json is not None,
            "created_at":       str(self.created_at) if self.created_at else None,
        }

