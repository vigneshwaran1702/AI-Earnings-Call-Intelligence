from pydantic import BaseModel
from typing import Optional, List


class FinancialHighlight(BaseModel):
    metric: str
    value: str
    change: Optional[str] = None
    source_quote: Optional[str] = None


class SummarySection(BaseModel):
    title: str
    content: str
    evidence: List[str] = []


class EarningsSummary(BaseModel):
    company: str
    quarter: str
    call_date: Optional[str] = None
    executive_summary: str
    financial_highlights: List[FinancialHighlight] = []
    sections: List[SummarySection] = []
    sentiment: Optional[str] = None           # bullish / bearish / neutral
    key_risks: List[str] = []
    management_guidance: Optional[str] = None
    source_transcript_id: Optional[int] = None


class TranscriptResponse(BaseModel):
    id: int
    company: str
    symbol: Optional[str]
    exchange: str
    quarter: Optional[str]
    call_date: Optional[str]
    title: Optional[str]
    source_url: Optional[str]
    processed: bool
    has_summary: bool
    created_at: Optional[str]

    class Config:
        from_attributes = True

