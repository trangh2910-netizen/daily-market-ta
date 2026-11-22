"""Fetch, deduplicate, time-filter, and beginner-annotate daily economic & geopolitical news."""

from __future__ import annotations

import calendar
import re
from datetime import datetime, timedelta
from typing import Any

import feedparser
import requests
from bs4 import BeautifulSoup

from config import RSS_FEEDS, VN_TZ

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; DailyMarketTA/1.0)"}

HIGH_IMPACT_KEYWORDS = [
    # Macro & monetary policy (VI)
    "lãi suất", "tỷ giá", "lạm phát", "ngân hàng nhà nước", "fed", "gdp",
    "vn-index", "chứng khoán", "khối ngoại", "trái phiếu", "tín dụng",
    "vàng", "giá dầu", "thuế quan", "xuất khẩu", "nhập khẩu", "fdi",
    "bất động sản", "đầu tư công", "nợ công", "thanh khoản", "cổ phiếu",
    # Geopolitics (VI)
    "chiến tranh", "xung đột", "trừng phạt", "nato", "trung đông", "mỹ - trung",
    "thuế nhập khẩu", "nga", "ukraine", "tổng thống", "chính phủ", "bầu cử",
    # English macro/geopolitics
    "rate", "inflation", "fed", "central bank", "tariff", "economy", "gdp",
    "oil", "gold", "stock", "market", "trade", "recession", "sanction", "bond",
]

NOISE_KEYWORDS = [
    "rau xanh", "hoa hậu", "ca sĩ", "diễn viên", "bóng đá", "tai nạn",
    "thời tiết", "xổ số", "ẩm thực", "du lịch", "showbiz", "ly hôn",
]

TOPIC_EXPLANATIONS = [
    (
        ["lãi suất", "fed", "ngân hàng nhà nước", "tín dụng", "rate", "central bank"],
        "Lãi suất là 'giá của đồng tiền'. Khi lãi suất tăng, vay vốn đắt đỏ hơn và tiền gửi tiết kiệm hấp dẫn hơn nên chứng khoán thường chịu áp lực; ngược lại lãi suất giảm giúp tiền rẻ chảy vào cổ phiếu.",
        "neutral",
    ),
    (
        ["tỷ giá", "usd", "đô la", "ngoại tệ"],
        "Khi tỷ giá USD/VND tăng mạnh, Ngân hàng Nhà nước có thể phải hút bớt tiền về để giữ ổn định, điều này thường khiến dòng tiền ngắn hạn trên chứng khoán thận trọng hơn.",
        "caution",
    ),
    (
        ["khối ngoại", "bán ròng", "mua ròng", "vn-index", "cổ phiếu", "chứng khoán"],
        "Dòng tiền của nhà đầu tư lớn và khối ngoại thường dẫn dắt tâm lý thị trường ngắn hạn.",
        "neutral",
    ),
    (
        ["vàng", "giá dầu", "oil", "gold", "xung đột", "chiến tranh", "trừng phạt", "thuế quan", "tariff"],
        "Bất ổn địa chính trị hoặc thuế quan thường đẩy giá vàng và dầu biến động mạnh, khiến nhà đầu tư có xu hướng tìm nơi trú ẩn an toàn thay vì mạo hiểm.",
        "caution",
    ),
    (
        ["đầu tư công", "xuất khẩu", "fdi", "gdp", "tăng trưởng", "cảng biển", "hạ tầng"],
        "Tin tức tăng trưởng sản xuất, hạ tầng và xuất khẩu là động lực dài hạn cho lợi nhuận doanh nghiệp niêm yết.",
        "positive",
    ),
]


def _clean_html(raw: str) -> str:
    if not raw:
        return ""
    text = BeautifulSoup(raw, "html.parser").get_text(" ", strip=True)
    return re.sub(r"\s+", " ", text).strip()


def _parse_entry_time(entry: Any, fallback_dt: datetime) -> datetime:
    parsed = getattr(entry, "published_parsed", None) or getattr(entry, "updated_parsed", None)
    if parsed:
        ts = calendar.timegm(parsed)
        return datetime.fromtimestamp(ts, tz=VN_TZ)
    return fallback_dt


def _score_article(title: str, summary: str, category: str) -> int:
    text = f"{title} {summary}".lower()
    if any(noise in text for noise in NOISE_KEYWORDS):
        return -10
    score = 0
    for kw in HIGH_IMPACT_KEYWORDS:
        if kw in text:
            score += 3
    if "chứng khoán" in category.lower() or "vĩ mô" in category.lower():
        score += 2
    return score


def _explain_impact(title: str, summary: str) -> tuple[str, str]:
    text = f"{title} {summary}".lower()
    for keywords, meaning, tone in TOPIC_EXPLANATIONS:
        if any(k in text for k in keywords):
            return meaning, tone
    return (
        "Tin tức vĩ mô giúp bạn hiểu bối cảnh dòng tiền và tâm lý chung của doanh nghiệp trong nước lẫn quốc tế.",
        "neutral",
    )


def fetch_daily_news(max_items: int = 8, hours_back: int = 48) -> list[dict[str, Any]]:
    """Fetch, filter by recency, rank by economic/geopolitical relevance, and deduplicate."""
    now_vn = datetime.now(VN_TZ)
    cutoff = now_vn - timedelta(hours=hours_back)
    raw_articles: list[dict[str, Any]] = []

    for feed_cfg in RSS_FEEDS:
        try:
            resp = requests.get(feed_cfg["url"], headers=HEADERS, timeout=10)
            resp.raise_for_status()
            parsed = feedparser.parse(resp.content)
            for entry in parsed.entries[:30]:
                title = _clean_html(getattr(entry, "title", ""))
                summary = _clean_html(getattr(entry, "summary", "") or getattr(entry, "description", ""))
                link = getattr(entry, "link", "")
                if not title or not link:
                    continue
                pub_dt = _parse_entry_time(entry, now_vn)
                if pub_dt < cutoff:
                    continue
                score = _score_article(title, summary, feed_cfg["category"])
                if score < 1:
                    continue
                meaning, tone = _explain_impact(title, summary)
                raw_articles.append(
                    {
                        "title": title,
                        "summary": summary[:260] + ("..." if len(summary) > 260 else ""),
                        "link": link,
                        "source": feed_cfg["source"],
                        "category": feed_cfg["category"],
                        "lang": feed_cfg["lang"],
                        "published_iso": pub_dt.isoformat(),
                        "published_vn": pub_dt.strftime("%H:%M %d/%m"),
                        "score": score,
                        "beginner_meaning": meaning,
                        "impact_tone": tone,
                    }
                )
        except Exception as exc:
            print(f"[WARN] Failed RSS {feed_cfg['source']}: {exc}")

    # Sort by relevance score + recency, then deduplicate similar titles
    raw_articles.sort(key=lambda x: (x["score"], x["published_iso"]), reverse=True)
    selected: list[dict[str, Any]] = []
    seen_prefixes: set[str] = set()

    for art in raw_articles:
        norm = re.sub(r"[^a-z0-9à-ỹ]+", " ", art["title"].lower()).strip()
        prefix = " ".join(norm.split()[:6])
        if prefix in seen_prefixes:
            continue
        seen_prefixes.add(prefix)
        selected.append(art)
        if len(selected) >= max_items:
            break

    return selected
