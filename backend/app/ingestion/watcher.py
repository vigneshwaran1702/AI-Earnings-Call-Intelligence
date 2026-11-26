"""
Concall Announcement Watcher

Collects announcements from both exchanges, filters for likely
earnings-call transcripts using keyword matching, normalizes
the results, and deduplicates by filing ID.
"""

import logging
import re
from app.ingestion.nse import get_nse_announcements
from app.ingestion.bse import get_bse_announcements

logger = logging.getLogger(__name__)

KEYWORDS = [
    "earnings call",
    "conference call",
    "concall",
    "transcript",
    "analyst meet",
    "investor meet",
    "investor call",
    "analyst call",
    "post results",
    "quarterly results",
    "earnings conference",
    "investor presentation",
]


def is_concall(item: dict) -> bool:
    """Check if an announcement is likely a concall transcript."""
    text = " ".join([
        str(item.get("title") or ""),
        str(item.get("category") or ""),
        str(item.get("company") or ""),
    ]).lower()
    return any(keyword in text for keyword in KEYWORDS)


def normalize_announcement(item: dict) -> dict:
    """Create a stable ID and consistent announcement fields."""
    filing_id = str(item.get("filing_id") or "").strip()
    url = str(item.get("source_url") or "").strip()

    if not filing_id:
        # Generate a deterministic ID from exchange + URL + title
        raw = f"{item.get('exchange', '')}-{url}-{item.get('title', '')}"
        filing_id = f"GEN-{hash(raw) & 0xFFFFFFFF:08x}"

    # Guess the quarter from the title or date
    quarter = _guess_quarter(
        item.get("title", ""),
        item.get("call_date", ""),
    )

    return {
        "company":    str(item.get("company") or "Unknown").strip(),
        "symbol":     str(item.get("symbol") or "").strip().upper(),
        "exchange":   str(item.get("exchange") or "").strip().upper(),
        "filing_id":  filing_id,
        "title":      str(item.get("title") or "").strip(),
        "category":   str(item.get("category") or "").strip(),
        "source_url": url,
        "call_date":  str(item.get("call_date") or "").strip(),
        "quarter":    quarter,
    }


def _guess_quarter(title: str, call_date: str) -> str:
    """Try to extract a quarter label like 'Q3 FY25' from text."""
    text = f"{title} {call_date}".upper()

    # Look for Q1/Q2/Q3/Q4 patterns
    match = re.search(r"(Q[1-4])\s*(FY\s*\d{2,4})?", text)
    if match:
        q = match.group(1)
        fy = match.group(2) or ""
        return f"{q} {fy}".strip()

    # Look for quarter mentions
    for label, q in [
        ("FIRST QUARTER", "Q1"), ("SECOND QUARTER", "Q2"),
        ("THIRD QUARTER", "Q3"), ("FOURTH QUARTER", "Q4"),
    ]:
        if label in text:
            return q

    return ""


def collect_concall_announcements(days_back: int = 7) -> list[dict]:
    """
    Main collection function: fetch from both exchanges,
    filter for concalls, normalize, and deduplicate.
    """
    all_announcements: list[dict] = []

    # ── NSE ────────────────────────────────────────────────────────
    try:
        nse_items = get_nse_announcements(days_back=days_back)
        logger.info("NSE: %d total announcements", len(nse_items))
        all_announcements.extend(nse_items)
    except Exception as exc:
        logger.error("NSE collection failed: %s", exc)

    # ── BSE ────────────────────────────────────────────────────────
    try:
        bse_items = get_bse_announcements()
        logger.info("BSE: %d total announcements", len(bse_items))
        all_announcements.extend(bse_items)
    except Exception as exc:
        logger.error("BSE collection failed: %s", exc)

    # ── Filter for concall-related ─────────────────────────────────
    concall_items = [item for item in all_announcements if is_concall(item)]
    logger.info(
        "Filtered %d concall announcements from %d total",
        len(concall_items), len(all_announcements),
    )

    # ── Normalize ──────────────────────────────────────────────────
    normalized = [normalize_announcement(item) for item in concall_items]

    # ── Deduplicate by filing_id ───────────────────────────────────
    seen: set[str] = set()
    unique: list[dict] = []
    for item in normalized:
        fid = item["filing_id"]
        if fid not in seen:
            seen.add(fid)
            unique.append(item)

    logger.info("After dedup: %d unique concall announcements", len(unique))
    return unique


# ── CLI entry point ────────────────────────────────────────────────
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
    )
    results = collect_concall_announcements()

    if not results:
        print("\nNo concall announcements found in the current window.")
        print("This may be normal — earnings season is periodic.\n")
    else:
        print(f"\n{'='*60}")
        print(f"Found {len(results)} possible concall announcements")
        print(f"{'='*60}\n")

        for item in results[:15]:
            print(f"  [{item['exchange']}] {item['company']}")
            print(f"    Title:   {item['title'][:80]}")
            print(f"    Quarter: {item['quarter'] or '—'}")
            print(f"    URL:     {item['source_url'][:80] if item['source_url'] else '—'}")
            print()

