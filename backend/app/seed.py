"""
Seed realistic sample earnings-call transcripts and PDFs for all tracked companies.
Usage:
    $env:PYTHONPATH="backend"
    python -m app.seed
"""

import json
import fitz  # PyMuPDF
from app.config import TRACKED_COMPANIES, TRANSCRIPT_DIR, SUMMARY_DIR
from app.database import SessionLocal, init_db
from app.models.transcript import Transcript


SAMPLE_DATA = {
    "TCS": {
        "exchange": "NSE",
        "quarter": "Q3 FY26",
        "call_date": "2026-01-12",
        "title": "TCS Q3 FY26 Earnings Conference Call Transcript",
        "sentiment": "Bullish",
        "revenue": "₹65,210 Cr (+5.6% YoY)",
        "pat": "₹12,480 Cr (+8.2% YoY)",
        "margin": "24.8% Operating Margin",
        "guidance": "Management expects BFSI recovery in North America and sustained GenAI deal pipeline momentum into FY27.",
        "highlights": [
            {"metric": "Revenue", "value": "₹65,210 Cr", "change": "+5.6% YoY", "source_quote": "Q3 revenue grew 5.6% YoY to ₹65,210 crore, led by BFSI and Consumer Business."},
            {"metric": "Operating Margin", "value": "24.8%", "change": "+40 bps QoQ", "source_quote": "Disciplined pyramid optimization helped expand operating margin to 24.8%."},
            {"metric": "Net Profit (PAT)", "value": "₹12,480 Cr", "change": "+8.2% YoY", "source_quote": "Net income stood at ₹12,480 crore with strong cash conversion."},
            {"metric": "Total Contract Value (TCV)", "value": "$10.2B", "change": "+12% YoY", "source_quote": "Order book TCV reached $10.2 billion in Q3, including two mega-deals."},
        ],
        "risks": [
            "Discretionary IT spending caution in European retail",
            "Wage inflation and visa-related cost pressures in North America",
        ],
    },
    "INFY": {
        "exchange": "NSE",
        "quarter": "Q3 FY26",
        "call_date": "2026-01-15",
        "title": "Infosys Q3 FY26 Earnings Call & Analyst Transcript",
        "sentiment": "Bullish",
        "revenue": "₹41,764 Cr (+6.1% YoY)",
        "pat": "₹6,890 Cr (+7.5% YoY)",
        "margin": "21.3% Operating Margin",
        "guidance": "FY26 constant-currency revenue growth guidance raised to 4.5%–5.0% on strong Topaz AI adoption.",
        "highlights": [
            {"metric": "Revenue", "value": "₹41,764 Cr", "change": "+6.1% YoY", "source_quote": "Broad-based growth across Financial Services and Manufacturing drove ₹41,764 Cr revenue."},
            {"metric": "Operating Margin", "value": "21.3%", "change": "+20 bps QoQ", "source_quote": "Project Maximus delivered operating margin of 21.3%."},
            {"metric": "Large Deal TCV", "value": "$2.5B", "change": "62% net new", "source_quote": "We signed 21 large deals totaling $2.5 billion, with 62% net new."},
            {"metric": "Free Cash Flow", "value": "$1.1B", "change": "+18% YoY", "source_quote": "Free cash flow generation remained robust at $1.1 billion."},
        ],
        "risks": [
            "Macro uncertainty in telecom and hi-tech verticals",
            "Cross-currency headwinds impacting reported USD growth",
        ],
    },
    "HDFCBANK": {
        "exchange": "BSE",
        "quarter": "Q3 FY26",
        "call_date": "2026-01-18",
        "title": "HDFC Bank Q3 FY26 Post-Results Conference Call Transcript",
        "sentiment": "Neutral",
        "revenue": "₹31,240 Cr NII (+8.4% YoY)",
        "pat": "₹17,650 Cr (+9.1% YoY)",
        "margin": "3.48% Net Interest Margin",
        "guidance": "Focus remains on improving Credit-Deposit ratio toward pre-merger levels while protecting asset quality.",
        "highlights": [
            {"metric": "Net Interest Income", "value": "₹31,240 Cr", "change": "+8.4% YoY", "source_quote": "NII grew 8.4% YoY to ₹31,240 crore on steady retail loan growth."},
            {"metric": "Net Interest Margin", "value": "3.48%", "change": "+3 bps QoQ", "source_quote": "Core NIM improved modestly to 3.48% as deposit mix normalized."},
            {"metric": "Gross NPA", "value": "1.34%", "change": "-2 bps QoQ", "source_quote": "Asset quality remained pristine with GNPA at 1.34%."},
            {"metric": "Deposit Growth", "value": "15.2% YoY", "change": "+₹62,000 Cr QoQ", "source_quote": "Deposits grew 15.2% YoY, outpacing loan growth."},
        ],
        "risks": [
            "Tight systemic liquidity keeping term deposit rates elevated",
            "Unsecured retail credit normalization across industry",
        ],
    },
    "ICICIBANK": {
        "exchange": "NSE",
        "quarter": "Q3 FY26",
        "call_date": "2026-01-20",
        "title": "ICICI Bank Q3 FY26 Earnings Conference Call Transcript",
        "sentiment": "Bullish",
        "revenue": "₹20,890 Cr NII (+11.2% YoY)",
        "pat": "₹11,920 Cr (+14.8% YoY)",
        "margin": "4.29% Net Interest Margin",
        "guidance": "Management confident of sustaining RoA above 2.3% backed by SME and business banking momentum.",
        "highlights": [
            {"metric": "Net Interest Income", "value": "₹20,890 Cr", "change": "+11.2% YoY", "source_quote": "NII rose 11.2% YoY to ₹20,890 crore."},
            {"metric": "Net Profit (PAT)", "value": "₹11,920 Cr", "change": "+14.8% YoY", "source_quote": "PAT grew 14.8% YoY to ₹11,920 crore with controlled opex."},
            {"metric": "Net Interest Margin", "value": "4.29%", "change": "Stable QoQ", "source_quote": "NIM held steady at 4.29% despite deposit repricing."},
            {"metric": "Net NPA", "value": "0.41%", "change": "-2 bps YoY", "source_quote": "Net NPA ratio improved to 0.41% with strong provisioning."},
        ],
        "risks": [
            "Gradual moderation in NIM if policy rate cuts accelerate",
            "Competitive pricing in prime corporate lending",
        ],
    },
    "RELIANCE": {
        "exchange": "NSE",
        "quarter": "Q3 FY26",
        "call_date": "2026-01-22",
        "title": "Reliance Industries Q3 FY26 Analyst & Investor Call Transcript",
        "sentiment": "Bullish",
        "revenue": "₹2,48,500 Cr (+7.8% YoY)",
        "pat": "₹21,350 Cr (+11.5% YoY)",
        "margin": "18.1% Consolidated EBITDA Margin",
        "guidance": "Jio 5G monetization and New Energy gigafactory commissioning on track for H2 CY26.",
        "highlights": [
            {"metric": "Consolidated Revenue", "value": "₹2,48,500 Cr", "change": "+7.8% YoY", "source_quote": "Consolidated revenue reached ₹2.48 lakh crore, led by Digital Services and Retail."},
            {"metric": "Consolidated EBITDA", "value": "₹44,980 Cr", "change": "+10.4% YoY", "source_quote": "EBITDA crossed ₹44,980 crore with 18.1% margin."},
            {"metric": "Jio ARPU", "value": "₹206", "change": "+13.2% YoY", "source_quote": "Jio ARPU rose to ₹206 following tariff flow-through and 5G upgrades."},
            {"metric": "Retail Revenue", "value": "₹89,400 Cr", "change": "+9.2% YoY", "source_quote": "Reliance Retail delivered ₹89,400 crore revenue across 19,100+ stores."},
        ],
        "risks": [
            "Global refining margin volatility in O2C segment",
            "High capex cycle in new energy and AI data centers",
        ],
    },
    "TATAMOTORS": {
        "exchange": "BSE",
        "quarter": "Q3 FY26",
        "call_date": "2026-01-25",
        "title": "Tata Motors Q3 FY26 Earnings Conference Call Transcript",
        "sentiment": "Neutral",
        "revenue": "₹1,14,200 Cr (+4.3% YoY)",
        "pat": "₹6,940 Cr (+5.1% YoY)",
        "margin": "14.2% Consolidated EBITDA Margin",
        "guidance": "JLR net debt-zero target remains on track; domestic EV portfolio expanding with two new launches.",
        "highlights": [
            {"metric": "Consolidated Revenue", "value": "₹1,14,200 Cr", "change": "+4.3% YoY", "source_quote": "Consolidated revenue stood at ₹1,14,200 crore."},
            {"metric": "JLR EBIT Margin", "value": "8.9%", "change": "+30 bps YoY", "source_quote": "JLR delivered 8.9% EBIT margin aided by Range Rover mix."},
            {"metric": "India CV EBITDA", "value": "11.6%", "change": "+50 bps YoY", "source_quote": "Commercial vehicles margin expanded to 11.6% on realization gains."},
            {"metric": "Net Auto Debt", "value": "₹14,800 Cr", "change": "-38% YoY", "source_quote": "Net automotive debt reduced significantly to ₹14,800 crore."},
        ],
        "risks": [
            "Softness in European and Chinese luxury auto demand",
            "Supply-chain disruptions affecting aluminum availability",
        ],
    },
    "SUNPHARMA": {
        "exchange": "NSE",
        "quarter": "Q3 FY26",
        "call_date": "2026-01-28",
        "title": "Sun Pharma Q3 FY26 Earnings Conference Call Transcript",
        "sentiment": "Bullish",
        "revenue": "₹13,850 Cr (+10.9% YoY)",
        "pat": "₹2,980 Cr (+15.4% YoY)",
        "margin": "28.4% EBITDA Margin",
        "guidance": "Global specialty portfolio (Ilumya, Winlevi, Cequa) expected to drive double-digit growth.",
        "highlights": [
            {"metric": "Total Revenue", "value": "₹13,850 Cr", "change": "+10.9% YoY", "source_quote": "Revenue grew 10.9% YoY to ₹13,850 crore."},
            {"metric": "Global Specialty Sales", "value": "$325M", "change": "+17.5% YoY", "source_quote": "Global specialty revenue reached $325 million, led by Ilumya."},
            {"metric": "India Formulations", "value": "₹4,310 Cr", "change": "+12.1% YoY", "source_quote": "India business outperformed IPM with 12.1% growth."},
            {"metric": "EBITDA Margin", "value": "28.4%", "change": "+110 bps YoY", "source_quote": "Operating leverage lifted EBITDA margin to 28.4%."},
        ],
        "risks": [
            "US FDA compliance observations at manufacturing facilities",
            "Pricing erosion in US generic dermatology products",
        ],
    },
}


def build_transcript_text(company_name: str, symbol: str, data: dict) -> str:
    """Create a realistic multi-section earnings call transcript."""
    hl_lines = "\n".join(
        f"  - {h['metric']}: {h['value']} ({h['change']}) — \"{h['source_quote']}\""
        for h in data["highlights"]
    )
    risk_lines = "\n".join(f"  - {r}" for r in data["risks"])
    return f"""{company_name} ({symbol}) — {data['quarter']} Earnings Conference Call Transcript
Exchange: {data['exchange']} | Call Date: {data['call_date']}
====================================================================

1. PARTICIPANTS
Management: Managing Director & CEO, Chief Financial Officer, Head of Investor Relations
Analysts: Institutional Equity Research Analysts (Domestic & Global Funds)

2. OPENING REMARKS & FINANCIAL PERFORMANCE
Good evening everyone, and welcome to the {company_name} {data['quarter']} earnings conference call.
We are pleased to report another resilient quarter driven by disciplined execution and client trust.

Key Financial Metrics:
{hl_lines}

3. SEGMENTAL & OPERATIONAL HIGHLIGHTS
Across our core operating segments, demand visibility improved sequentially. Digital transformation,
operational efficiency, and disciplined capital allocation remained central to our strategy during
{data['quarter']}. Management highlighted strong customer retention and healthy pipeline conversion.

4. MANAGEMENT GUIDANCE & OUTLOOK
{data['guidance']}

5. KEY RISKS & WATCHLIST
{risk_lines}

6. Q&A HIGHLIGHTS
Analyst (Motilal Oswal): Could you elaborate on margin sustainability heading into Q4 and FY27?
CFO: Our margin trajectory is supported by productivity levers, utilization, and favorable mix.
We remain focused on balancing growth investments with healthy free cash flow generation.

Analyst (Morgan Stanley): How is the demand environment in key international and domestic markets?
CEO: Client conversations are constructive, with larger multi-year programs moving from pilot to scale.

[End of Transcript — Finosauras Intelligence Sample Dataset]
"""


def build_summary_payload(company_name: str, data: dict) -> tuple[dict, str]:
    """Build 7-section structured summary JSON and Markdown."""
    sections = [
        {
            "title": "1. Executive Summary",
            "content": f"{company_name} delivered a {data['sentiment'].lower()} {data['quarter']} performance with {data['revenue']} and {data['pat']}.",
            "evidence": [h["source_quote"] for h in data["highlights"][:2]],
        },
        {
            "title": "2. Financial Performance",
            "content": f"Revenue: {data['revenue']} | PAT: {data['pat']} | Margin: {data['margin']}.",
            "evidence": [h["source_quote"] for h in data["highlights"]],
        },
        {
            "title": "3. Segmental & Operational Drivers",
            "content": f"Core verticals showed steady momentum with strong order/customer traction during {data['quarter']}.",
            "evidence": [data["highlights"][0]["source_quote"]],
        },
        {
            "title": "4. Management Guidance & Outlook",
            "content": data["guidance"],
            "evidence": [data["guidance"]],
        },
        {
            "title": "5. Capital Allocation & Cash Flow",
            "content": "Healthy cash generation and disciplined balance-sheet management continued through the quarter.",
            "evidence": [data["highlights"][-1]["source_quote"]],
        },
        {
            "title": "6. Key Risks & Headwinds",
            "content": "; ".join(data["risks"]),
            "evidence": data["risks"],
        },
        {
            "title": "7. Analyst Q&A Takeaways",
            "content": "Analysts focused on margin durability, demand recovery, and medium-term capital efficiency.",
            "evidence": ["Management reiterated focus on balancing growth investments with free cash flow."],
        },
    ]

    summary_dict = {
        "company": company_name,
        "quarter": data["quarter"],
        "call_date": data["call_date"],
        "executive_summary": sections[0]["content"],
        "financial_highlights": data["highlights"],
        "sections": sections,
        "sentiment": data["sentiment"],
        "key_risks": data["risks"],
        "management_guidance": data["guidance"],
    }

    md_parts = [f"# {company_name} — {data['quarter']} AI Earnings Summary\n"]
    for sec in sections:
        md_parts.append(f"## {sec['title']}\n{sec['content']}\n")
    summary_md = "\n".join(md_parts)

    return summary_dict, summary_md


def create_pdf(filepath, text: str) -> None:
    """Render transcript text into a clean multi-page PDF using PyMuPDF."""
    doc = fitz.open()
    lines = text.splitlines()
    page = doc.new_page(width=595, height=842)  # A4
    y = 50
    for line in lines:
        if y > 790:
            page = doc.new_page(width=595, height=842)
            y = 50
        is_heading = line.startswith(("1.", "2.", "3.", "4.", "5.", "6.")) or "===" in line
        fontsize = 11 if is_heading else 9.5
        page.insert_text((45, y), line[:105], fontsize=fontsize, fontname="helv")
        y += 16 if is_heading else 13
    doc.save(filepath)
    doc.close()


def seed_all() -> int:
    init_db()
    db = SessionLocal()
    inserted = 0

    try:
        for comp in TRACKED_COMPANIES:
            symbol = comp["symbol"]
            name = comp["name"]
            data = SAMPLE_DATA[symbol]
            filing_id = f"SAMPLE-{symbol}-{data['quarter'].replace(' ', '')}"

            pdf_filename = f"{symbol}_{data['quarter'].replace(' ', '_')}.pdf"
            pdf_path = TRANSCRIPT_DIR / pdf_filename
            raw_text = build_transcript_text(name, symbol, data)
            create_pdf(pdf_path, raw_text)

            summary_dict, summary_md = build_summary_payload(name, data)

            # Save markdown copy in data/summaries/
            (SUMMARY_DIR / f"{symbol}_{data['quarter'].replace(' ', '_')}.md").write_text(
                summary_md, encoding="utf-8"
            )

            existing = db.query(Transcript).filter(Transcript.filing_id == filing_id).first()
            if existing:
                existing.pdf_path = str(pdf_path)
                existing.raw_text = raw_text
                existing.summary_json = json.dumps(summary_dict)
                existing.summary_markdown = summary_md
                existing.processed = True
            else:
                record = Transcript(
                    company=name,
                    symbol=symbol,
                    exchange=data["exchange"],
                    filing_id=filing_id,
                    quarter=data["quarter"],
                    call_date=data["call_date"],
                    title=data["title"],
                    source_url=f"/api/transcripts/pdf/{pdf_filename}",
                    pdf_path=str(pdf_path),
                    raw_text=raw_text,
                    summary_json=json.dumps(summary_dict),
                    summary_markdown=summary_md,
                    processed=True,
                )
                db.add(record)
                inserted += 1

        db.commit()
    finally:
        db.close()

    print(f"Seeded {len(TRACKED_COMPANIES)} companies ({inserted} new records) with PDFs in {TRANSCRIPT_DIR}")
    return inserted


if __name__ == "__main__":
    seed_all()

