"""Prompt templates for structured Indian earnings-call summarization."""

SYSTEM_PROMPT = (
    "You are an institutional Indian equity research analyst. "
    "Analyze earnings call transcripts accurately and return strictly valid JSON "
    "with exact quotes from the transcript as supporting evidence."
)


def build_chunk_prompt(company: str, quarter: str, chunk: str, idx: int, total: int) -> str:
    return (
        f"Extract key financial metrics, segmental commentary, management guidance, "
        f"risks, and analyst Q&A takeaways from part {idx}/{total} of {company} ({quarter}) "
        f"earnings call transcript. Include verbatim quotes as evidence.\n\n"
        f"TRANSCRIPT PART {idx}/{total}:\n{chunk}"
    )


def build_final_summary_prompt(company: str, quarter: str, call_date: str, content: str) -> str:
    return f"""Produce a structured JSON earnings call summary for {company} ({quarter}, Call Date: {call_date}).
Return ONLY valid JSON matching this exact schema:
{{
  "company": "{company}",
  "quarter": "{quarter}",
  "call_date": "{call_date}",
  "executive_summary": "2-3 sentence overview",
  "sentiment": "Bullish | Neutral | Bearish",
  "management_guidance": "Key forward guidance",
  "key_risks": ["risk 1", "risk 2"],
  "financial_highlights": [
    {{"metric": "Revenue", "value": "...", "change": "...", "source_quote": "exact quote"}}
  ],
  "sections": [
    {{"title": "1. Executive Summary", "content": "...", "evidence": ["exact quote"]}},
    {{"title": "2. Financial Performance", "content": "...", "evidence": ["exact quote"]}},
    {{"title": "3. Segmental & Operational Drivers", "content": "...", "evidence": ["exact quote"]}},
    {{"title": "4. Management Guidance & Outlook", "content": "...", "evidence": ["exact quote"]}},
    {{"title": "5. Capital Allocation & Cash Flow", "content": "...", "evidence": ["exact quote"]}},
    {{"title": "6. Key Risks & Headwinds", "content": "...", "evidence": ["exact quote"]}},
    {{"title": "7. Analyst Q&A Takeaways", "content": "...", "evidence": ["exact quote"]}}
  ]
}}

SOURCE CONTENT:
{content}
"""
