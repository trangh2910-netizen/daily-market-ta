"""Main pipeline: fetch market & news, generate TA charts, script, MP3 podcast, web app, and optional email.

Supports three modes:
  - python main.py                         (full automated run; uses Gemini API if key set, else local engine)
  - python main.py --prepare-only          (fetch data/news + draw charts -> write docs/pending_context.json)
  - python main.py --publish-file <path>   (use AI-authored briefing JSON -> synthesize MP3 + build docs/index.html)
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from audio_generator import generate_podcast_audio
from chart_generator import render_annotated_chart
from config import BASE_DIR, DOCS_DIR, EPISODES_DIR, STATE_FILE, VN_TZ
from market_data import collect_all_market_data
from news_fetcher import fetch_daily_news
from notifier import send_daily_email
from script_writer import build_daily_briefing
from ta_curriculum import select_lesson_and_case_study
from ta_file_generator import generate_ta_lesson_file
from tiktok_generator import render_tiktok_video
from web_builder import build_web_site

PENDING_CONTEXT_PATH = BASE_DIR / "pending_context.json"


def _strip_private_keys(obj: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in obj.items() if not k.startswith("_")}


def _load_state() -> dict[str, Any]:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"lesson_index": 0, "last_run_date": ""}


def _save_state(state: dict[str, Any]) -> None:
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def _load_existing_episodes() -> list[dict[str, Any]]:
    archive_file = DOCS_DIR / "archive.json"
    if archive_file.exists():
        try:
            data = json.loads(archive_file.read_text(encoding="utf-8"))
            if isinstance(data, list):
                return data
        except Exception:
            pass
    return []


def prepare_context() -> dict[str, Any]:
    """Steps 1-4: collect real market/news data, pick TA lesson, render charts, and save context JSON."""
    now_vn = datetime.now(VN_TZ)
    today_iso = now_vn.strftime("%Y-%m-%d")

    state = _load_state()
    lesson_index = int(state.get("lesson_index", 0))
    if state.get("last_run_date") and state["last_run_date"] != today_iso:
        lesson_index += 1

    print(f"[1/4] Collecting market data ({today_iso})...")
    market_data = collect_all_market_data()

    print("[2/4] Fetching recent economic & political news...")
    news = fetch_daily_news(max_items=8, hours_back=48)

    print(f"[3/4] Selecting TA lesson #{lesson_index + 1} and matching chart...")
    lesson, case_stock = select_lesson_and_case_study(market_data["stocks"], lesson_index)

    ep_dir = EPISODES_DIR / today_iso
    ep_dir.mkdir(parents=True, exist_ok=True)

    print("[4/4] Rendering annotated TA charts...")
    vni_chart_path = ep_dir / "vnindex.png"
    render_annotated_chart(
        market_data["vnindex"],
        vni_chart_path,
        subtitle="Tổng quan chỉ số VN-Index + Đường trung bình MA20/MA50 + RSI",
        focus="ma20",
    )

    lesson_chart_rel = ""
    if case_stock:
        lesson_chart_path = ep_dir / "lesson_chart.png"
        render_annotated_chart(
            case_stock,
            lesson_chart_path,
            subtitle=f"Minh họa {lesson['title']}",
            focus=lesson["focus_indicator"],
        )
        lesson_chart_rel = f"./episodes/{today_iso}/lesson_chart.png"

    context = {
        "episode_id": today_iso,
        "lesson_index": lesson_index,
        "generated_at": market_data["generated_at"],
        "generated_date_vn": market_data["generated_date_vn"],
        "generated_time_vn": market_data["generated_time_vn"],
        "market_trade_date_vn": market_data["market_trade_date_vn"],
        "is_weekend_or_closed": market_data["is_weekend_or_closed"],
        "vnindex": _strip_private_keys(market_data["vnindex"]),
        "stocks": [_strip_private_keys(s) for s in market_data["stocks"]],
        "macro": market_data["macro"],
        "news": news,
        "lesson": lesson,
        "case_stock_symbol": case_stock["symbol"] if case_stock else None,
        "case_stock": _strip_private_keys(case_stock) if case_stock else None,
        "vni_chart_rel_path": f"./episodes/{today_iso}/vnindex.png",
        "lesson_chart_rel_path": lesson_chart_rel,
    }
    PENDING_CONTEXT_PATH.write_text(json.dumps(context, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[PREPARED] Context saved to: {PENDING_CONTEXT_PATH}")
    return context


def publish_episode(context: dict[str, Any], briefing: dict[str, Any]) -> Path:
    """Steps 5-6: synthesize MP3 podcast, update docs/index.html, save state, and send optional email."""
    today_iso = context["episode_id"]
    ep_dir = EPISODES_DIR / today_iso
    ep_dir.mkdir(parents=True, exist_ok=True)

    print("[5/7] Synthesizing podcast audio...")
    audio_path = generate_podcast_audio(briefing["podcast_script"], ep_dir)

    print("[6/7] Rendering 9:16 TikTok/Shorts video & bilingual TA study file...")
    tiktok_rel = ""
    try:
        tiktok_path = ep_dir / "tiktok_today.mp4"
        render_tiktok_video(context, ep_dir, tiktok_path)
        tiktok_rel = f"./episodes/{today_iso}/tiktok_today.mp4"
    except Exception as exc:
        print(f"[WARN] TikTok video render skipped: {exc}")

    lesson_chart_file = ep_dir / "lesson_chart.png"
    ta_file_path = ep_dir / "ta_lesson.html"
    generate_ta_lesson_file(
        context,
        briefing,
        lesson_chart_file if lesson_chart_file.exists() else None,
        ta_file_path,
    )
    ta_file_rel = f"./episodes/{today_iso}/ta_lesson.html"

    episode_record = {
        "episode_id": today_iso,
        "generated_at": context["generated_at"],
        "generated_date_vn": context["generated_date_vn"],
        "generated_time_vn": context["generated_time_vn"],
        "market_trade_date_vn": context["market_trade_date_vn"],
        "is_weekend_or_closed": context["is_weekend_or_closed"],
        "vnindex": context["vnindex"],
        "stocks": context["stocks"],
        "macro": context["macro"],
        "news": context["news"],
        "lesson": context["lesson"],
        "case_stock_symbol": context["case_stock_symbol"],
        "briefing": briefing,
        "vni_chart_rel_path": context["vni_chart_rel_path"],
        "lesson_chart_rel_path": context["lesson_chart_rel_path"],
        "audio_rel_path": f"./episodes/{today_iso}/{audio_path.name}",
        "tiktok_rel_path": tiktok_rel,
        "ta_file_rel_path": ta_file_rel,
    }

    existing = [ep for ep in _load_existing_episodes() if ep.get("episode_id") != today_iso]
    episodes = [episode_record] + existing
    episodes = episodes[:30]

    print("[7/7] Building web app in docs/...")
    index_path = build_web_site(episodes)

    _save_state({"lesson_index": context["lesson_index"], "last_run_date": today_iso})
    charts_to_attach = [ep_dir / "vnindex.png"]
    if (ep_dir / "lesson_chart.png").exists():
        charts_to_attach.append(ep_dir / "lesson_chart.png")
    ta_attachment_name = f"TA_Bai_{context['lesson']['id']}_{today_iso}.html"
    send_daily_email(
        briefing,
        {
            "vnindex": context["vnindex"],
            "macro": context.get("macro", []),
            "stocks": context.get("stocks", []),
            "news": context.get("news", []),
        },
        context["lesson"],
        audio_path,
        charts_to_attach,
        ta_file_path=ta_file_path,
        ta_attachment_name=ta_attachment_name,
    )
    print(f"[DONE] Web app ready at: {index_path}")
    return index_path


def run_pipeline(prepare_only: bool = False, publish_file: str | None = None) -> None:
    if publish_file:
        context = json.loads(PENDING_CONTEXT_PATH.read_text(encoding="utf-8"))
        briefing = json.loads(Path(publish_file).read_text(encoding="utf-8"))
        briefing.setdefault("mode", "antigravity_agent")
        publish_episode(context, briefing)
        return

    context = prepare_context()
    if prepare_only:
        return

    briefing = build_daily_briefing(
        {
            "generated_at": context["generated_at"],
            "generated_date_vn": context["generated_date_vn"],
            "generated_time_vn": context["generated_time_vn"],
            "market_trade_date_vn": context["market_trade_date_vn"],
            "is_weekend_or_closed": context["is_weekend_or_closed"],
            "vnindex": context["vnindex"],
            "stocks": context["stocks"],
            "macro": context["macro"],
        },
        context["news"],
        context["lesson"],
        context["case_stock"],
    )
    publish_episode(context, briefing)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Daily Market & TA Podcast pipeline")
    parser.add_argument("--prepare-only", action="store_true", help="Fetch data/news & draw charts only")
    parser.add_argument("--publish-file", type=str, default=None, help="Publish from an agent-authored briefing JSON")
    args = parser.parse_args()
    run_pipeline(prepare_only=args.prepare_only, publish_file=args.publish_file)
