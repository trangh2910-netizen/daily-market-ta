"""Detailed Gmail SMTP notifier sending rich market briefing, watchlist table, TA lesson, charts, and MP3."""

from __future__ import annotations

import smtplib
from email.message import EmailMessage
from pathlib import Path
from typing import Any

from config import NOTIFY_EMAIL, PUBLIC_SITE_URL, SMTP_PASS, SMTP_USER


def _fmt_price(val: float | None, is_index: bool = False) -> str:
    if val is None:
        return "-"
    return f"{val:,.2f}" if is_index else f"{val:,.0f} đ"


def send_daily_email(
    briefing: dict[str, Any],
    market_data: dict[str, Any],
    lesson: dict[str, Any],
    audio_path: Path | None = None,
    chart_paths: list[Path] | None = None,
    video_path: Path | None = None,
    ta_file_path: Path | None = None,
    ta_attachment_name: str | None = None,
    en_audio_path: Path | None = None,
) -> bool:
    """Send a comprehensive, beginner-friendly daily briefing email with charts and MP3 attached."""
    if not (SMTP_USER and SMTP_PASS and NOTIFY_EMAIL):
        print("[INFO] Email notification skipped (SMTP_USER/SMTP_PASS/NOTIFY_EMAIL not set).")
        return False

    vni = market_data["vnindex"]
    macro_list = market_data.get("macro", [])
    stocks = market_data.get("stocks", [])
    raw_news = market_data.get("news", [])

    macro_cells = "".join(
        f"<td style='padding:8px 10px;border:1px solid #cbd5e1;background:#f8fafc;'>"
        f"<div style='font-size:11px;color:#64748b;'>{m['label']}</div>"
        f"<div style='font-weight:bold;font-size:14px;'>{m['close']:,.2f}" if isinstance(m['close'], float) and m.get('decimals', 0) > 0 else
        f"<td style='padding:8px 10px;border:1px solid #cbd5e1;background:#f8fafc;'><div style='font-size:11px;color:#64748b;'>{m['label']}</div><div style='font-weight:bold;font-size:14px;'>{m['close']:,.0f}"
        + f"</div><div style='font-size:12px;color:{'#16a34a' if m['change_pct'] > 0 else ('#dc2626' if m['change_pct'] < 0 else '#d97706')};'>{m['change_pct']:+.2f}%</div></td>"
        for m in macro_list
        if m.get("close") is not None
    )

    news_insights = briefing.get("news_insights") or []
    if news_insights:
        news_items_html = "".join(
            f"<li style='margin-bottom:12px;'>"
            f"<div style='font-weight:bold;color:#0f172a;'>{n.get('title','')}</div>"
            f"<div style='font-size:13.5px;color:#334155;margin-top:3px;'><strong>Vì sao &amp; Tác động:</strong> {n.get('so_what','')}</div>"
            f"</li>"
            for n in news_insights
        )
    else:
        news_items_html = "".join(
            f"<li style='margin-bottom:12px;'>"
            f"<div style='font-weight:bold;color:#0f172a;'>{n['title']} <span style='font-weight:normal;font-size:12px;color:#64748b;'>({n['source']})</span></div>"
            f"<div style='font-size:13.5px;color:#334155;margin-top:3px;'><strong>Vì sao quan trọng:</strong> {n['beginner_meaning']}</div>"
            f"</li>"
            for n in raw_news[:5]
        )

    stock_rows = "".join(
        f"<tr>"
        f"<td style='padding:7px;border-bottom:1px solid #e2e8f0;'><strong>{s['symbol']}</strong><br/><span style='font-size:11px;color:#64748b;'>{s['name']}</span></td>"
        f"<td style='padding:7px;border-bottom:1px solid #e2e8f0;'>{_fmt_price(s['close'])}</td>"
        f"<td style='padding:7px;border-bottom:1px solid #e2e8f0;color:{'#16a34a' if s['change_pct'] > 0 else ('#dc2626' if s['change_pct'] < 0 else '#d97706')};font-weight:bold;'>{s['change_pct']:+.2f}%</td>"
        f"<td style='padding:7px;border-bottom:1px solid #e2e8f0;font-size:12.5px;'><strong>{s['status_label']}</strong> (RSI {s['rsi14']:.0f}, Vol {s['vol_ratio']:.1f}x)<br/><span style='color:#475569;'>{s['beginner_note']}</span></td>"
        f"</tr>"
        for s in stocks
    )

    deep_dive_html = (
        f"<p style='background:#f8fafc;border-left:4px solid #0284c7;padding:10px 12px;font-size:14px;color:#1e293b;'>"
        f"<strong>🔍 Giải mã dòng tiền hôm nay:</strong> {briefing['market_deep_dive']}</p>"
        if briefing.get("market_deep_dive")
        else ""
    )

    quiz = lesson.get("quiz", {})
    quiz_opts = "".join(f"<li>{opt}</li>" for opt in quiz.get("options", []))
    ans_idx = quiz.get("answer_index", 0)
    ans_text = quiz.get("options", [""])[ans_idx] if quiz.get("options") else ""

    uni_examples = briefing.get("uni_exam_examples") or []
    uni_html = ""
    if uni_examples:
        uni_items = "".join(
            f"<li style='margin-bottom:10px;'>"
            f"<strong>[{ex.get('subject','')}]</strong> <em>{ex.get('concept','')}</em><br/>"
            f"<span style='color:#334155;'>👉 Ví dụ viết bài tự luận: {ex.get('essay_example','')}</span>"
            f"</li>"
            for ex in uni_examples
        )
        uni_html = (
            "<h3 style='color:#1e293b;border-bottom:1px solid #cbd5e1;padding-bottom:4px;'>"
            "📚 4. Kho Ví Dụ Thi Tự Luận Cuối Kỳ (Liên hệ môn học hôm nay)</h3>"
            f"<ul style='padding-left:18px;font-size:13.5px;background:#fefce8;padding-top:10px;padding-bottom:10px;border-radius:10px;'>{uni_items}</ul>"
        )

    en = briefing.get("english_summary") or {}
    en_html = ""
    if en:
        vocab_items = "".join(
            f"<li><strong>{v.get('term','')}</strong> ({v.get('vn','')}): {v.get('meaning','')}</li>"
            for v in (en.get("vocab") or [])
        )
        en_script_block = (
            f"<p style='margin:8px 0;background:#ffffff;padding:10px;border-radius:8px;border:1px solid #bfdbfe;'>"
            f"<strong>🎧 Transcript để vừa nghe <code>english_listening.mp3</code> vừa dò chữ:</strong><br/>"
            f"{en.get('listening_script_en','')}</p>"
            if en.get("listening_script_en")
            else ""
        )
        en_html = (
            "<h3 style='color:#1e293b;border-bottom:1px solid #cbd5e1;padding-bottom:4px;'>"
            "🇬🇧 5. Luyện Nghe Tiếng Anh Cơ Bản &amp; Từ Vựng (English Listening)</h3>"
            f"<div style='background:#eff6ff;padding:12px;border-radius:10px;font-size:13.5px;border-left:4px solid #2563eb;'>"
            f"<div><strong>{en.get('headline_en','')}</strong></div>"
            f"<p style='margin:6px 0;'>{en.get('market_summary_en','')}</p>"
            f"<p style='margin:6px 0;'><em>TA Note:</em> {en.get('ta_lesson_en','')}</p>"
            f"{en_script_block}"
            f"{f'<ul style=\"padding-left:18px;margin:6px 0;\">{vocab_items}</ul>' if vocab_items else ''}"
            "</div>"
        )

    bb = briefing.get("brain_booster") or {}
    bb_html = ""
    if bb.get("insight"):
        bb_html = (
            "<h3 style='color:#1e293b;border-bottom:1px solid #cbd5e1;padding-bottom:4px;'>"
            f"⚡ 6. Góc Thông Não Hôm Nay ({bb.get('theme', '')})</h3>"
            "<div style='background:#f5f3ff;padding:12px;border-radius:10px;font-size:13.5px;border-left:4px solid #7c3aed;'>"
            f"<div style='font-weight:bold;color:#5b21b6;'>{bb.get('title','')}</div>"
            f"<p style='margin:6px 0 0;color:#334155;'>{bb.get('insight','')}</p>"
            "</div>"
        )

    site_cta = (
        f'<p style="margin:20px 0;"><a href="{PUBLIC_SITE_URL}" '
        f'style="background:#0284c7;color:#ffffff;padding:12px 20px;border-radius:8px;text-decoration:none;font-weight:bold;display:inline-block;">'
        f'Mở Web App &amp; Video TikTok hôm nay</a></p>'
        if PUBLIC_SITE_URL
        else ""
    )

    html_body = f"""
    <div style="font-family:Arial,sans-serif;max-width:680px;margin:auto;color:#0f172a;line-height:1.6;">
      <h2 style="color:#0369a1;margin-bottom:4px;">📊 {briefing['headline']}</h2>
      <p style="color:#475569;font-size:14px;">{briefing['intro_note']}</p>

      <div style="background:#f1f5f9;padding:14px;border-radius:10px;margin:14px 0;">
        <strong>VN-Index (phiên {vni['trade_date_vn']}):</strong> {vni['close']:,.2f} điểm ({vni['change_pct']:+.2f}%) — <em>{vni['status_label']}</em><br/>
        <span style="font-size:13px;color:#334155;">{vni['beginner_note']} (RSI: {vni['rsi14']:.0f} | MA20: {_fmt_price(vni.get('ma20'), True)})</span>
      </div>

      {f"<table style='width:100%;border-collapse:collapse;margin:12px 0;'><tr>{macro_cells}</tr></table>" if macro_cells else ""}

      <h3 style="color:#1e293b;border-bottom:1px solid #cbd5e1;padding-bottom:4px;">📰 1. Tin Kinh tế – Chính trị &amp; Lý do tác động</h3>
      <ul style="padding-left:18px;font-size:14px;">{news_items_html}</ul>

      <h3 style="color:#1e293b;border-bottom:1px solid #cbd5e1;padding-bottom:4px;">📈 2. Soi chi tiết Watchlist</h3>
      {deep_dive_html}
      {f"<table style='width:100%;border-collapse:collapse;font-size:13px;'><thead><tr style='background:#f1f5f9;text-align:left;'><th style='padding:7px;'>Mã</th><th style='padding:7px;'>Giá</th><th style='padding:7px;'>Đổi</th><th style='padding:7px;'>Giải thích dễ hiểu</th></tr></thead><tbody>{stock_rows}</tbody></table>" if stock_rows else ""}

      <h3 style="color:#1e293b;border-bottom:1px solid #cbd5e1;padding-bottom:4px;">🎓 3. Lớp học TA: {lesson['title']}</h3>
      <p style="font-size:14px;">{lesson['concept_plain']}</p>
      <p style="background:#eff6ff;padding:12px;border-radius:10px;font-size:14px;">
        <strong>👀 Soi từng chi tiết trên biểu đồ đính kèm:</strong> {briefing.get('case_walkthrough', '')}
      </p>
      <div style="background:#f8fafc;padding:12px;border-radius:10px;border:1px solid #cbd5e1;font-size:13.5px;">
        <strong>✅ Mini Quiz tự kiểm tra:</strong> {quiz.get('question', '')}
        <ol type="A" style="margin:6px 0;">{quiz_opts}</ol>
        <div style="color:#475569;font-size:12.5px;margin-top:6px;"><em>Đáp án: {ans_text} — {quiz.get('explanation', '')}</em></div>
      </div>

      {uni_html}

      {en_html}

      {bb_html}

      {site_cta}
      <p style="font-size:13px;color:#64748b;margin-top:16px;">📎 <strong>Đính kèm sẵn ngay trong email:</strong> file nghe tiếng Việt <strong>podcast.mp3</strong>, file luyện nghe Tiếng Anh <strong>english_listening.mp3</strong>, <strong>file tài liệu TA (.html)</strong>, và <strong>2 ảnh biểu đồ chú thích</strong>.</p>
    </div>
    """

    msg = EmailMessage()
    msg["Subject"] = f"📊 {briefing['headline']}"
    msg["From"] = SMTP_USER
    msg["To"] = NOTIFY_EMAIL
    msg.set_content(f"{briefing['headline']}\n\n{briefing['intro_note']}\n\n{PUBLIC_SITE_URL}")
    msg.add_alternative(html_body, subtype="html")

    if audio_path and audio_path.exists():
        subtype = "wav" if audio_path.suffix.lower() == ".wav" else "mpeg"
        msg.add_attachment(
            audio_path.read_bytes(),
            maintype="audio",
            subtype=subtype,
            filename=audio_path.name,
        )

    for chart_p in chart_paths or []:
        if chart_p and chart_p.exists():
            msg.add_attachment(
                chart_p.read_bytes(),
                maintype="image",
                subtype="png",
                filename=chart_p.name,
            )

    if en_audio_path and en_audio_path.exists():
        subtype = "wav" if en_audio_path.suffix.lower() == ".wav" else "mpeg"
        msg.add_attachment(
            en_audio_path.read_bytes(),
            maintype="audio",
            subtype=subtype,
            filename=en_audio_path.name,
        )

    if ta_file_path and ta_file_path.exists():
        msg.add_attachment(
            ta_file_path.read_bytes(),
            maintype="text",
            subtype="html",
            filename=ta_attachment_name or ta_file_path.name,
        )

    if video_path and video_path.exists() and video_path.stat().st_size <= 15 * 1024 * 1024:
        msg.add_attachment(
            video_path.read_bytes(),
            maintype="video",
            subtype="mp4",
            filename=video_path.name,
        )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=120) as smtp:
        smtp.login(SMTP_USER, SMTP_PASS)
        smtp.send_message(msg)

    print(f"[OK] Sent detailed daily email to {NOTIFY_EMAIL}")
    return True
