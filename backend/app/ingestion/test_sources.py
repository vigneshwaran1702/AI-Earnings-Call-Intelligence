"""
Ingestion Test Report

Runs all collectors and prints a diagnostic summary.
Usage:
    $env:PYTHONPATH="backend"
    python -m app.ingestion.test_sources
"""

import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

from app.ingestion.nse import get_nse_announcements
from app.ingestion.bse import get_bse_announcements
from app.ingestion.watcher import collect_concall_announcements
from app.ingestion.downloader import download_pdf


def main():
    print("\n" + "=" * 60)
    print("  FINOSAURAS — INGESTION TEST REPORT")
    print("=" * 60)

    # ── NSE ─────────────────────────────────────────────────────────
    print("\n──── NSE TEST ────")
    nse = get_nse_announcements(days_back=7)
    print(f"  NSE announcements fetched: {len(nse)}")
    for item in nse[:3]:
        print(f"    • {item['company'][:40]} — {item['title'][:50]}")

    # ── BSE ─────────────────────────────────────────────────────────
    print("\n──── BSE TEST ────")
    bse = get_bse_announcements()
    print(f"  BSE announcements fetched: {len(bse)}")
    for item in bse[:3]:
        print(f"    • {item['company'][:40]} — {item['title'][:50]}")

    # ── Concall filter ──────────────────────────────────────────────
    print("\n──── CONCALL FILTER ────")
    calls = collect_concall_announcements()
    print(f"  Possible concall filings: {len(calls)}")
    for item in calls[:10]:
        print(f"\n    Company:  {item['company']}")
        print(f"    Exchange: {item['exchange']}")
        print(f"    Title:    {item['title'][:70]}")
        print(f"    Quarter:  {item['quarter'] or '—'}")
        print(f"    URL:      {item['source_url'][:70] if item['source_url'] else '—'}")

    # ── PDF download test ───────────────────────────────────────────
    print("\n──── PDF DOWNLOAD TEST ────")
    downloaded = False
    for item in calls:
        url = item.get("source_url", "")
        if url.lower().split("?")[0].endswith(".pdf"):
            result = download_pdf(url, item["filing_id"])
            print(f"  Download result: {result}")
            if result:
                downloaded = True
                break

    if not downloaded:
        print("  No downloadable PDF found in current announcements.")
        print("  This is normal outside earnings season.")

    # ── Summary ─────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("  SUMMARY")
    print("=" * 60)
    print(f"  NSE announcements:    {len(nse)}")
    print(f"  BSE announcements:    {len(bse)}")
    print(f"  Concall candidates:   {len(calls)}")
    print(f"  PDF downloaded:       {'Yes' if downloaded else 'No'}")
    print(f"  Pipeline status:      {'✓ Working' if (nse or bse) else '⚠ No data (may be blocked)'}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()

