"""
NSE Corporate Announcements Collector

Uses NSE's public website announcement endpoint to fetch recent
equity announcements. This is an undocumented website endpoint,
not a guaranteed public developer API — session access and response
fields can change without notice.
"""

from datetime import date, timedelta
from typing import Any
import logging
import requests

logger = logging.getLogger(__name__)

BASE_URL = "https://www.nseindia.com"
API_URL = f"{BASE_URL}/api/corporate-announcements"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/140.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Referer": (
        f"{BASE_URL}/companies-listing/"
        "corporate-filings-announcements"
    ),
}

session = requests.Session()
session.headers.update(HEADERS)


def _warm_session() -> None:
    """
    Visit the NSE homepage first to get cookies.
    NSE blocks API calls without a valid session cookie.
    """
    try:
        resp = session.get(BASE_URL, timeout=10)
        resp.raise_for_status()
        logger.debug("NSE session warmed — cookies: %s", list(session.cookies.keys()))
    except Exception as exc:
        logger.warning("NSE session warmup failed: %s", exc)


def get_nse_announcements(days_back: int = 7) -> list[dict[str, Any]]:
    """Fetch recent equity announcements from NSE."""
    end_date = date.today()
    start_date = end_date - timedelta(days=days_back)

    params = {
        "index": "equities",
        "from_date": start_date.strftime("%d-%m-%Y"),
        "to_date": end_date.strftime("%d-%m-%Y"),
    }

    _warm_session()

    try:
        response = session.get(API_URL, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.JSONDecodeError:
        logger.error(
            "NSE returned non-JSON (status %s). "
            "The endpoint may be blocked or changed.",
            response.status_code,
        )
        return []
    except requests.exceptions.RequestException as exc:
        logger.error("NSE request failed: %s", exc)
        return []

    announcements: list[dict[str, Any]] = []

    # NSE returns a list of announcement objects
    items = data if isinstance(data, list) else data.get("data", [])

    for item in items:
        try:
            company = (
                item.get("companyName")
                or item.get("company_name")
                or item.get("sm_name")
                or ""
            ).strip()

            symbol = (
                item.get("symbol")
                or item.get("sm_key")
                or ""
            ).strip()

            title = (
                item.get("desc")
                or item.get("subject")
                or item.get("smDesc")
                or ""
            ).strip()

            category = (
                item.get("an_type")
                or item.get("category")
                or item.get("smIndustry")
                or ""
            ).strip()

            # Attachment URL
            attachment = (
                item.get("attchmntFile")
                or item.get("attachment")
                or ""
            ).strip()

            if attachment and not attachment.startswith("http"):
                attachment = f"https://nsearchives.nseindia.in/corporate/Attachments/{attachment}"

            filing_id = (
                item.get("an_id")
                or item.get("seq_id")
                or f"nse-{symbol}-{hash(title) & 0xFFFFFF:06x}"
            )

            call_date = (
                item.get("an_dt")
                or item.get("dt")
                or item.get("bm_date")
                or ""
            ).strip()

            announcements.append({
                "company": company,
                "symbol": symbol,
                "exchange": "NSE",
                "filing_id": f"NSE-{filing_id}",
                "title": title,
                "category": category,
                "source_url": attachment,
                "call_date": call_date,
                "raw": item,
            })
        except Exception as exc:
            logger.debug("Skipping malformed NSE item: %s", exc)
            continue

    logger.info("NSE returned %d announcements", len(announcements))
    return announcements

