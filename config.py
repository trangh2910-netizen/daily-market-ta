"""Central configuration for Daily Market & TA Tutor."""

from __future__ import annotations

import os
from datetime import timezone, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DOCS_DIR = BASE_DIR / "docs"
EPISODES_DIR = DOCS_DIR / "episodes"
STATE_FILE = BASE_DIR / "state.json"

VN_TZ = timezone(timedelta(hours=7))

# Vietnamese blue-chip stocks for daily tracking and real-chart TA lessons
VN_WATCHLIST = [
    {"symbol": "FPT", "name": "FPT Corp", "sector": "Công nghệ"},
    {"symbol": "HPG", "name": "Hòa Phát", "sector": "Thép"},
    {"symbol": "VCB", "name": "Vietcombank", "sector": "Ngân hàng"},
    {"symbol": "TCB", "name": "Techcombank", "sector": "Ngân hàng"},
    {"symbol": "SSI", "name": "Chứng khoán SSI", "sector": "Chứng khoán"},
    {"symbol": "MWG", "name": "Thế Giới Di Động", "sector": "Bán lẻ"},
    {"symbol": "VHM", "name": "Vinhomes", "sector": "Bất động sản"},
    {"symbol": "MBB", "name": "MB Bank", "sector": "Ngân hàng"},
]

MACRO_SYMBOLS = [
    {"symbol": "^GSPC", "label": "S&P 500 (Mỹ)", "unit": "điểm", "decimals": 2},
    {"symbol": "GC=F", "label": "Vàng Thế Giới", "unit": "USD/oz", "decimals": 1},
    {"symbol": "USDVND=X", "label": "Tỷ giá USD/VND", "unit": "VND", "decimals": 0},
    {"symbol": "BTC-USD", "label": "Bitcoin", "unit": "USD", "decimals": 0},
]

RSS_FEEDS = [
    {
        "source": "VnExpress Kinh doanh",
        "category": "Kinh tế VN",
        "url": "https://vnexpress.net/rss/kinh-doanh.rss",
        "lang": "vi",
    },
    {
        "source": "CafeF Chứng khoán",
        "category": "Chứng khoán",
        "url": "https://cafef.vn/thi-truong-chung-khoan.rss",
        "lang": "vi",
    },
    {
        "source": "CafeF Tài chính Quốc tế",
        "category": "Vĩ mô Quốc tế",
        "url": "https://cafef.vn/tai-chinh-quoc-te.rss",
        "lang": "vi",
    },
    {
        "source": "VnExpress Thế giới",
        "category": "Chính trị - Địa chính trị",
        "url": "https://vnexpress.net/rss/the-gioi.rss",
        "lang": "vi",
    },
    {
        "source": "BBC Business",
        "category": "Kinh tế Toàn cầu",
        "url": "https://feeds.bbci.co.uk/news/business/rss.xml",
        "lang": "en",
    },
]

# Voice options: Gemini 3.8 Flash TTS (when GEMINI_API_KEY is set) -> edge-tts -> gTTS
GEMINI_TTS_MODEL = os.environ.get("GEMINI_TTS_MODEL", "gemini-3.8-flash-tts")
GEMINI_TTS_VOICE = os.environ.get("GEMINI_TTS_VOICE", "Puck")
GEMINI_TTS_STYLE = os.environ.get(
    "GEMINI_TTS_STYLE",
    "cheerful, witty, upbeat, lively Northern Vietnamese (Hanoi) male podcast host",
)
TTS_VOICE = os.environ.get("TTS_VOICE", "vi-VN-NamMinhNeural")
TTS_RATE = os.environ.get("TTS_RATE", "+8%")

# Optional Gemini API key for richer natural-language news synthesis (grounded strictly in fetched JSON)
def _load_dotenv_key(key: str) -> str:
    env_file = BASE_DIR / ".env"
    if not env_file.exists():
        return ""
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        if k.strip() == key:
            return v.strip().strip('"').strip("'")
    return ""


GEMINI_API_KEY = (os.environ.get("GEMINI_API_KEY", "").strip() or _load_dotenv_key("GEMINI_API_KEY"))
GEMINI_MODEL = (os.environ.get("GEMINI_MODEL", "").strip() or _load_dotenv_key("GEMINI_MODEL"))
GEMINI_FALLBACK_MODELS = [
    m for m in [GEMINI_MODEL, "gemini-4-hydrogen", "gemini-3.1-pro-preview", "gemini-3.6-flash", "gemini-2.5-flash"] if m
]

# Optional Email notification settings (Gmail SMTP)
SMTP_USER = (os.environ.get("SMTP_USER", "").strip() or _load_dotenv_key("SMTP_USER"))
SMTP_PASS = (os.environ.get("SMTP_PASS", "").strip() or _load_dotenv_key("SMTP_PASS"))
NOTIFY_EMAIL = (os.environ.get("NOTIFY_EMAIL", "").strip() or _load_dotenv_key("NOTIFY_EMAIL"))
PUBLIC_SITE_URL = (os.environ.get("PUBLIC_SITE_URL", "").strip() or _load_dotenv_key("PUBLIC_SITE_URL"))
