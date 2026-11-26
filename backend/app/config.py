import os
from pathlib import Path
from dotenv import load_dotenv

# ── Paths ──────────────────────────────────────────────────────────
ROOT_DIR = Path(__file__).resolve().parents[2]          # AI cell/
load_dotenv(ROOT_DIR / ".env")

DATA_DIR        = ROOT_DIR / "data"
TRANSCRIPT_DIR  = DATA_DIR / "transcripts"
SUMMARY_DIR     = DATA_DIR / "summaries"

for folder in (TRANSCRIPT_DIR, SUMMARY_DIR):
    folder.mkdir(parents=True, exist_ok=True)

# ── Database ───────────────────────────────────────────────────────
_db_url_env = os.getenv("DATABASE_URL", "")
DATABASE_URL = (
    _db_url_env if _db_url_env.strip()
    else f"sqlite:///{(ROOT_DIR / 'finosauras.db').as_posix()}"
)

# ── AI ─────────────────────────────────────────────────────────────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

# ── Exchange base URLs ─────────────────────────────────────────────
NSE_BASE_URL = "https://www.nseindia.com"
BSE_BASE_URL = "https://www.bseindia.com"

# ── Tracked companies ─────────────────────────────────────────────
TRACKED_COMPANIES = [
    {"name": "TCS",                   "symbol": "TCS",        "scrip_code": "532540"},
    {"name": "Infosys",               "symbol": "INFY",       "scrip_code": "500209"},
    {"name": "HDFC Bank",             "symbol": "HDFCBANK",   "scrip_code": "500180"},
    {"name": "ICICI Bank",            "symbol": "ICICIBANK",  "scrip_code": "532174"},
    {"name": "Reliance Industries",   "symbol": "RELIANCE",   "scrip_code": "500325"},
    {"name": "Tata Motors",           "symbol": "TATAMOTORS", "scrip_code": "500570"},
    {"name": "Sun Pharma",            "symbol": "SUNPHARMA",  "scrip_code": "524715"},
]

# ── Concall detection keywords ────────────────────────────────────
CONCALL_KEYWORDS = [
    "earnings call",
    "concall",
    "conference call",
    "analyst meet",
    "investor call",
    "quarterly results",
    "earnings conference",
    "post results",
    "transcript",
    "investor presentation",
]

# ── Scheduler ──────────────────────────────────────────────────────
POLL_INTERVAL_MINUTES = int(os.getenv("POLL_INTERVAL_MINUTES", "30"))

