"""
BSE Announcements Collector

Uses BSE's public latest-announcements RSS feed as the initial source.
This is a different integration from NSE's JSON endpoint.
The feed is public but not a complete historical search API —
it shows only the most recent announcements.
"""

import logging
import re
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

BSE_FEED_URL = "https://www.bseindia.com/data/xml/announcements.xml"
BSE_ANN_API = "https://api.bseindia.com/BseIndiaAPI/api/AnnSubCategoryGetData/w"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 Chrome/140.0.0.0 Safari/537.36"
    ),
    "Accept": "application/rss+xml, application/xml, text/xml, */*",
}

JSON_HEADERS = {
    "User-Agent": HEADERS["User-Agent"],
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.bseindia.com/corporates/ann.html",
    "Origin": "https://www.bseindia.com",
}


def get_bse_announcements() -> list[dict]:
    """Read latest BSE announcements from its RSS feed."""
    try:
        response = requests.get(
            BSE_FEED_URL,
            headers=HEADERS,
            timeout=30,
        )
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "xml")
        results = []

        for item in soup.find_all("item"):
            title = item.title.get_text(" ", strip=True) if item.title else ""
            link = item.link.get_text(strip=True) if item.link else ""
            pub_date = item.pubDate.get_text(strip=True) if item.pubDate else ""
            description = (
                item.description.get_text(" ", strip=True)
                if item.description
                else ""
            )

            # Try to extract company name and scrip code from title/description
            company = _extract_company(title, description)
            scrip_code = _extract_scrip_code(link, description)
            symbol = _extract_symbol(title, description)

            # Build a stable filing ID from BSE
            filing_id = _extract_filing_id(link, title)

            results.append({
                "company": company,
                "symbol": symbol,
                "exchange": "BSE",
                "filing_id": f"BSE-{filing_id}",
                "title": title,
                "category": _extract_category(title, description),
                "source_url": link,
                "call_date": pub_date,
                "scrip_code": scrip_code,
                "raw": {
                    "title": title,
                    "link": link,
                    "pubDate": pub_date,
                    "description": description,
                },
            })

        logger.info("BSE feed returned %d announcements", len(results))
        return results

    except requests.exceptions.RequestException as exc:
        logger.error("BSE feed request failed: %s", exc)
        return []
    except Exception as exc:
        logger.error("BSE feed parsing failed: %s", exc)
        return []


def get_bse_announcements_api(
    scrip_code: str = "",
    days_back: int = 7,
) -> list[dict]:
    """
    Alternative: use BSE's JSON API for announcements.
    Falls back gracefully if the endpoint is unavailable.
    """
    from datetime import date, timedelta

    end_date = date.today()
    start_date = end_date - timedelta(days=days_back)

    params = {
        "strCat": "-1",
        "strPrevDate": start_date.strftime("%Y%m%d"),
        "strScrip": scrip_code,
        "strSearch": "P",
        "strTodayDate": end_date.strftime("%Y%m%d"),
        "strType": "C",
    }

    try:
        response = requests.get(
            BSE_ANN_API,
            params=params,
            headers=JSON_HEADERS,
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
    except Exception as exc:
        logger.error("BSE API request failed: %s", exc)
        return []

    if not isinstance(data, dict) or "Table" not in data:
        logger.warning("BSE API returned unexpected format")
        return []

    results = []
    for item in data.get("Table", []):
        attachment = item.get("ATTACHMENTNAME", "")
        if attachment and not attachment.startswith("http"):
            attachment = f"https://www.bseindia.com/xml-data/corpfiling/AttachHis/{attachment}"

        results.append({
            "company": item.get("SLONGNAME", "").strip(),
            "symbol": item.get("SCRIP_CD", "").strip(),
            "exchange": "BSE",
            "filing_id": f"BSE-{item.get('NEWSID', '')}",
            "title": item.get("NEWSSUB", "").strip(),
            "category": item.get("CATEGORYNAME", "").strip(),
            "source_url": attachment,
            "call_date": item.get("NEWS_DT", "").strip(),
            "scrip_code": str(item.get("SCRIP_CD", "")),
            "raw": item,
        })

    logger.info("BSE API returned %d announcements", len(results))
    return results


# ── Helpers ────────────────────────────────────────────────────────

def _extract_company(title: str, description: str) -> str:
    """Best-effort company name extraction."""
    # Often title starts with company name before a dash or colon
    for text in (title, description):
        match = re.match(r"^([A-Za-z][A-Za-z0-9&\s.,'()-]+?)[\s]*[-–:|]", text)
        if match:
            return match.group(1).strip()
    return title[:80].strip() if title else "Unknown"


def _extract_scrip_code(link: str, description: str) -> str:
    for text in (link, description):
        match = re.search(r"(?:scrip(?:code)?|sc)=(\d{5,6})", text, re.IGNORECASE)
        if match:
            return match.group(1)
    return ""


def _extract_symbol(title: str, description: str) -> str:
    for text in (title, description):
        match = re.search(r"\b([A-Z]{2,15})\b", text)
        if match and match.group(1) not in ("BSE", "NSE", "LTD", "THE", "AND"):
            return match.group(1)
    return ""


def _extract_filing_id(link: str, title: str) -> str:
    match = re.search(r"(?:newsid|ann_id|id)=(\d+)", link, re.IGNORECASE)
    if match:
        return match.group(1)
    return f"{hash(title) & 0xFFFFFFFF:08x}"


def _extract_category(title: str, description: str) -> str:
    text = f"{title} {description}".lower()
    if "result" in text or "financial" in text:
        return "Financial Results"
    if "board meeting" in text:
        return "Board Meeting"
    if "transcript" in text or "concall" in text:
        return "Conference Call"
    return "General"

