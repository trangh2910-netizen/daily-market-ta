"""Generate a self-contained, bilingual (Vietnamese + Simple English) TA study sheet HTML file."""

from __future__ import annotations

import base64
import html
from pathlib import Path
from typing import Any


def _img_to_data_uri(img_path: Path | None) -> str:
    if not img_path or not img_path.exists():
        return ""
    b64 = base64.b64encode(img_path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{b64}"


def generate_ta_lesson_file(
    context: dict[str, Any],
    briefing: dict[str, Any],
    lesson_chart_path: Path | None,
    output_path: Path,
) -> Path:
    """Create a standalone HTML TA study guide with embedded chart, plain-Vietnamese + English text, vocab, and quiz."""
    lesson = context["lesson"]
    en = briefing.get("english_summary") or {}
    sym = context.get("case_stock_symbol") or "VNINDEX"
    date_vn = context["generated_date_vn"]
    trade_date_vn = context["market_trade_date_vn"]

    chart_uri = _img_to_data_uri(lesson_chart_path)
    chart_block = (
        f'<img src="{chart_uri}" alt="TA Chart {html.escape(sym)}" style="width:100%;border-radius:12px;border:1px solid #cbd5e1;margin:12px 0;" />'
        if chart_uri
        else ""
    )

    vocab_rows = "".join(
        f"<tr>"
        f"<td style='padding:8px;border-bottom:1px solid #e2e8f0;'><strong>{html.escape(str(v.get('term','')))}</strong></td>"
        f"<td style='padding:8px;border-bottom:1px solid #e2e8f0;color:#0369a1;'>{html.escape(str(v.get('vn','')))}</td>"
        f"<td style='padding:8px;border-bottom:1px solid #e2e8f0;color:#334155;'>{html.escape(str(v.get('meaning','')))}</td>"
        f"</tr>"
        for v in (en.get("vocab") or [])
    )

    quiz = lesson.get("quiz", {})
    quiz_opts_html = "".join(
        f'<button class="qopt" onclick="checkAns(this, {idx}, {int(quiz.get("answer_index", 0))})">{html.escape(opt)}</button>'
        for idx, opt in enumerate(quiz.get("options", []))
    )

    html_doc = f"""<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{html.escape(lesson['title'])} — Tài liệu TA Song ngữ ({html.escape(date_vn)})</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif; background: #f8fafc; color: #0f172a; line-height: 1.65; margin: 0; padding: 20px; }}
    .wrap {{ max-width: 780px; margin: 0 auto; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 16px; padding: 24px; box-shadow: 0 4px 18px rgba(15,23,42,0.06); }}
    h1 {{ font-size: 1.4rem; color: #0369a1; margin: 0 0 6px; }}
    .meta {{ font-size: 0.88rem; color: #64748b; margin-bottom: 18px; }}
    .box {{ background: #f1f5f9; border-radius: 12px; padding: 14px 16px; margin: 14px 0; }}
    .box-en {{ background: #eff6ff; border-left: 4px solid #2563eb; border-radius: 10px; padding: 14px 16px; margin: 14px 0; }}
    h2 {{ font-size: 1.08rem; color: #1e293b; margin: 20px 0 8px; border-bottom: 1px solid #e2e8f0; padding-bottom: 4px; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 0.92rem; }}
    th {{ text-align: left; padding: 8px; background: #f1f5f9; color: #475569; }}
    .qopt {{ display: block; width: 100%; text-align: left; margin-top: 8px; padding: 10px 12px; border-radius: 8px; border: 1px solid #cbd5e1; background: #fff; cursor: pointer; font-size: 0.94rem; }}
    .qopt.ok {{ background: #dcfce7; border-color: #16a34a; font-weight: 600; }}
    .qopt.bad {{ background: #fee2e2; border-color: #dc2626; }}
  </style>
</head>
<body>
  <div class="wrap">
    <h1>📘 {html.escape(lesson['title'])}</h1>
    <div class="meta">Ngày {html.escape(date_vn)} · Dữ liệu phiên {html.escape(trade_date_vn)} · Cổ phiếu minh họa: <strong>{html.escape(sym)}</strong></div>

    <h2>1. Hiểu đơn giản bằng từ cơ bản (Tiếng Việt)</h2>
    <div class="box">
      <p style="margin:0 0 8px;"><strong>Khái niệm cốt lõi:</strong> {html.escape(lesson['concept_plain'])}</p>
      <p style="margin:0;"><strong>Cách nhìn trên biểu đồ:</strong> {html.escape(lesson['how_to_spot'])}</p>
    </div>

    <h2>2. Thực hành soi biểu đồ thật hôm nay ({html.escape(sym)})</h2>
    <p>{html.escape(briefing.get('case_walkthrough', ''))}</p>
    {chart_block}

    <h2>3. Phiên bản Tiếng Anh cơ bản (Simple English)</h2>
    <div class="box-en">
      <p style="margin:0 0 8px;"><strong>Topic:</strong> {html.escape(str(en.get('headline_en', lesson['title'])))}</p>
      <p style="margin:0 0 8px;"><strong>TA Lesson in Simple English:</strong> {html.escape(str(en.get('ta_lesson_en', '')))}</p>
      <p style="margin:0;"><strong>Market Recap:</strong> {html.escape(str(en.get('market_summary_en', '')))}</p>
    </div>

    {f"<h2>4. Từ vựng Tiếng Anh tài chính hôm nay</h2><table><thead><tr><th>English Term</th><th>Tiếng Việt</th><th>Giải thích đơn giản</th></tr></thead><tbody>{vocab_rows}</tbody></table>" if vocab_rows else ""}

    <h2>5. Kiểm tra nhanh (Mini Quiz)</h2>
    <div class="box">
      <div><strong>{html.escape(str(quiz.get('question','')))}</strong></div>
      <div id="opts">{quiz_opts_html}</div>
      <div id="exp" style="display:none;margin-top:10px;color:#0369a1;font-size:0.92rem;">💡 {html.escape(str(quiz.get('explanation','')))}</div>
    </div>
  </div>
  <script>
    function checkAns(btn, idx, ans) {{
      const all = document.querySelectorAll('.qopt');
      all.forEach((b, i) => {{
        b.classList.remove('ok', 'bad');
        if (i === ans) b.classList.add('ok');
        else if (i === idx) b.classList.add('bad');
      }});
      document.getElementById('exp').style.display = 'block';
    }}
  </script>
</body>
</html>
"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html_doc, encoding="utf-8")
    return output_path
