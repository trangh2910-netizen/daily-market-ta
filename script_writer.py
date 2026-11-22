"""Generate beginner-friendly market commentary and spoken podcast script grounded in verified data."""

from __future__ import annotations

import json
from typing import Any

from config import GEMINI_API_KEY, GEMINI_FALLBACK_MODELS


def _fmt_num(val: float | int | None, is_index: bool = False) -> str:
    if val is None:
        return "chưa có dữ liệu"
    if is_index:
        return f"{val:,.2f}".replace(",", ".")
    return f"{val:,.0f}".replace(",", ".")


def _fmt_spoken_pct(pct: float) -> str:
    direction = "tăng" if pct > 0 else ("giảm" if pct < 0 else "đi ngang")
    return f"{direction} {abs(pct):.2f} phần trăm".replace(".", " phẩy ")


def _build_case_study_walkthrough(lesson: dict[str, Any], stock: dict[str, Any] | None) -> str:
    if not stock:
        return lesson["concept_plain"]

    sym = stock["symbol"]
    name = stock["name"]
    price_str = _fmt_num(stock["close"], is_index=False)
    chg_str = _fmt_spoken_pct(stock["change_pct"])
    c = stock["candle"]

    candle_desc = (
        "một cây nến Doji thân rất mảnh, thể hiện phe Mua và phe Bán đang giằng co ngang ngửa"
        if c["is_doji"]
        else (
            "một cây nến Xanh, tức giá đóng cửa cao hơn lúc mở cửa"
            if c["color"] == "green"
            else "một cây nến Đỏ, tức cuối phiên giá bị bán thấp hơn lúc mở cửa"
        )
    )
    if c["is_hammer"]:
        candle_desc += ", đặc biệt có phần râu dưới khá dài cho thấy có lực đỡ khi giá giảm xuống thấp"
    elif c["is_shooting_star"]:
        candle_desc += ", kèm râu trên dài cho thấy khi giá kéo lên cao đã gặp áp lực chốt lời"

    ma20_desc = ""
    if stock["ma20"]:
        rel = "nằm trên" if stock["signals"]["above_ma20"] else "đang nằm dưới"
        ma20_desc = f" Giá hiện {rel} đường trung bình 20 ngày (MA20 ở mức {_fmt_num(stock['ma20'])} đồng)."

    return (
        f"Để dễ hình dung, bạn hãy mở biểu đồ mã {sym} ({name}) trong bản tin hôm nay. "
        f"Phiên gần nhất {sym} đóng cửa ở mức {price_str} đồng, {chg_str}. "
        f"Nhìn cây nến cuối cùng bên phải: đây là {candle_desc}.{ma20_desc} "
        f"Thanh khoản đạt khoảng {stock['vol_ratio']:.1f} lần mức trung bình 20 ngày, và chỉ số RSI đang ở mức {stock['rsi14']:.0f}."
    )


def _generate_local_briefing(
    market_data: dict[str, Any],
    news: list[dict[str, Any]],
    lesson: dict[str, Any],
    case_stock: dict[str, Any] | None,
) -> dict[str, Any]:
    """Deterministic, accurate, plain-Vietnamese tutor script when Gemini API key is not configured."""
    vni = market_data["vnindex"]
    date_vn = market_data["generated_date_vn"]
    trade_date_vn = market_data["market_trade_date_vn"]

    if market_data["is_weekend_or_closed"]:
        intro_market_note = (
            f"Hôm nay là {date_vn}, thị trường chứng khoán Việt Nam đang nghỉ giao dịch, "
            f"vì vậy chúng ta cùng nhìn lại bức tranh phiên giao dịch gần nhất ngày {trade_date_vn} "
            f"kết hợp với các tin tức kinh tế chính trị mới nhất."
        )
    else:
        intro_market_note = (
            f"Chào bạn, hôm nay là ngày {date_vn}. Đây là bản tin tổng hợp kinh tế, chính trị "
            f"và lớp học Phân tích kỹ thuật thực chiến theo dữ liệu phiên {trade_date_vn}."
        )

    # Part 1: News digest
    top_news = news[:3]
    if top_news:
        news_spoken_parts = ["Phần một: Điểm tin kinh tế và chính trị đáng chú ý."]
        for idx, art in enumerate(top_news, 1):
            news_spoken_parts.append(
                f"Tin thứ {idx} từ {art['source']}: {art['title']}. "
                f"Ý nghĩa cho người mới: {art['beginner_meaning']}"
            )
        news_spoken = " ".join(news_spoken_parts)
    else:
        news_spoken = "Phần một: Hôm nay chưa có biến động tin tức vĩ mô lớn từ các nguồn theo dõi."

    # Part 2: Market & Watchlist
    vni_chg = _fmt_spoken_pct(vni["change_pct"])
    vni_pos = "trên" if vni["signals"]["above_ma20"] else "dưới"
    macro_bits = []
    for m in market_data["macro"][:3]:
        if m.get("close") is not None:
            macro_bits.append(f"{m['label']} ở mức {m['close']} ({_fmt_spoken_pct(m['change_pct'])})")
    macro_text = (". Trên thế giới, " + "; ".join(macro_bits)) if macro_bits else ""

    stocks = market_data["stocks"]
    movers = sorted(stocks, key=lambda s: abs(s["change_pct"]), reverse=True)[:3]
    mover_lines = []
    for st in movers:
        mover_lines.append(
            f"Mã {st['symbol']} {st['name']} đóng cửa {_fmt_num(st['close'])} đồng, {_fmt_spoken_pct(st['change_pct'])}. "
            f"Trạng thái hiện tại: {st['status_label']}. {st['beginner_note']}"
        )

    market_spoken = (
        f"Phần hai: Soi thị trường chứng khoán. Chỉ số VN-Index phiên {trade_date_vn} đóng cửa ở {vni['close']:.2f} điểm, "
        f"{vni_chg}, hiện đang đứng {vni_pos} đường trung bình 20 ngày. "
        f"Đánh giá chung: {vni['beginner_note']}{macro_text}. "
        f"Trong danh sách theo dõi hôm nay: " + " ".join(mover_lines)
    )

    # Part 3: TA Lesson on Real Chart
    walkthrough = _build_case_study_walkthrough(lesson, case_stock)
    ta_spoken = (
        f"Phần ba: Mỗi ngày một chiêu Phân tích kỹ thuật. Chủ đề hôm nay là {lesson['title']}. "
        f"Kiến thức cốt lõi bạn cần nhớ: {lesson['concept_plain']} "
        f"Bây giờ hãy áp dụng ngay lên biểu đồ thật: {walkthrough} "
        f"Sau khi nghe xong, bạn lướt xuống phần bài tập trắc nghiệm nhanh bên dưới để kiểm tra xem mình đã nắm chắc bài hôm nay chưa nhé. Chúc bạn một ngày đầu tư tỉnh táo và nhiều năng lượng!"
    )

    podcast_script = f"{intro_market_note}\n\n{news_spoken}\n\n{market_spoken}\n\n{ta_spoken}"

    return {
        "mode": "local_tutor_engine",
        "headline": f"Bản tin & Lớp học TA ngày {date_vn} (Phiên {trade_date_vn})",
        "intro_note": intro_market_note,
        "podcast_script": podcast_script,
        "case_walkthrough": walkthrough,
    }


def _generate_gemini_briefing(
    market_data: dict[str, Any],
    news: list[dict[str, Any]],
    lesson: dict[str, Any],
    case_stock: dict[str, Any] | None,
) -> dict[str, Any]:
    """Use Gemini API strictly grounded in fetched market & news JSON."""
    from google import genai

    compact_stocks = [
        {
            "symbol": s["symbol"],
            "name": s["name"],
            "close": s["close"],
            "change_pct": s["change_pct"],
            "vol_ratio": s["vol_ratio"],
            "ma20": s["ma20"],
            "rsi14": s["rsi14"],
            "status": s["status_label"],
            "note": s["beginner_note"],
        }
        for s in market_data["stocks"]
    ]
    compact_news = [
        {"source": n["source"], "category": n["category"], "title": n["title"], "summary": n["summary"]}
        for n in news[:5]
    ]

    prompt_payload = {
        "today_vn": market_data["generated_date_vn"],
        "market_trade_date_vn": market_data["market_trade_date_vn"],
        "is_weekend_or_closed": market_data["is_weekend_or_closed"],
        "vnindex": {
            "close": market_data["vnindex"]["close"],
            "change_pct": market_data["vnindex"]["change_pct"],
            "rsi14": market_data["vnindex"]["rsi14"],
            "above_ma20": market_data["vnindex"]["signals"]["above_ma20"],
            "note": market_data["vnindex"]["beginner_note"],
        },
        "macro": market_data["macro"],
        "watchlist": compact_stocks,
        "news": compact_news,
        "today_ta_lesson": {
            "title": lesson["title"],
            "concept_plain": lesson["concept_plain"],
            "case_stock_symbol": case_stock["symbol"] if case_stock else None,
            "case_stock_data": next((c for c in compact_stocks if case_stock and c["symbol"] == case_stock["symbol"]), None),
        },
    }

    system_prompt = (
        "Bạn là một anh gia sư tài chính & phân tích kỹ thuật (TA) có phong cách DÍ DỎM, DỄ HIỂU nhưng TƯ DUY VĨ MÔ SÂU SẮC, KHÔNG NÓI CHUNG CHUNG HỜI HỢT, dành cho người mới muốn hiểu bản chất thị trường (F0).\n"
        "Hãy dựa 100% vào JSON dữ liệu thật dưới đây (TUYỆT ĐỐI KHÔNG tự bịa số liệu giá hay tin tức ngoài JSON) để viết:\n"
        "1) 'headline': tiêu đề ngắn gọn, bắt tai có ngày.\n"
        "2) 'intro_note': 2-3 câu mở đầu vui vẻ tóm tắt bối cảnh chung (nêu rõ nếu hôm nay thị trường nghỉ giao dịch thì đang tổng kết phiên nào và lý do cốt lõi khiến thị trường đang ở trạng thái đó).\n"
        "3) 'news_insights': danh sách 4-5 tin nổi bật từ JSON, mỗi tin gồm: 'title', 'so_what' (KHÔNG viết hời hợt; bắt buộc giải thích rõ 3 lớp: (a) Bản chất & nguyên nhân sự kiện, (b) Ảnh hưởng CỤ THỂ về Việt Nam như thế nào — tác động ra sao tới tỷ giá USD/VND, điều hành lãi suất của Ngân hàng Nhà nước, dòng vốn khối ngoại trên sàn Việt Nam, chi phí vốn/xuất nhập khẩu của doanh nghiệp VN, (c) Nhóm cổ phiếu Việt Nam nào chịu áp lực hay hưởng lợi như Ngân hàng, Bất động sản, Chứng khoán, Công nghệ, Thép, Bán lẻ/Xuất khẩu), 'tone' ('positive'|'caution'|'neutral').\n"
        "4) 'market_deep_dive': 5-6 câu phân tích sâu bức tranh VN-Index & các mã nổi bật trong watchlist (giải thích VÌ SAO dòng tiền lại chọn nhóm này, tránh nhóm kia, liên kết với tin vĩ mô, MA20/MA50, RSI, Volume).\n"
        "5) 'case_walkthrough': 5-6 câu hướng dẫn cực kỳ chi tiết từng bước để người mới nhìn vào biểu đồ mã minh họa của bài học TA hôm nay (chỉ rõ giá mở/đóng cửa, râu nến, vị trí so với MA20/MA50, volume và VÌ SAO hành động giá đó cho thấy tâm lý phe Mua/phe Bán).\n"
        "6) 'uni_exam_examples': danh sách 2 ví dụ thực tế (mỗi ví dụ là 1 object {'subject': '...', 'concept': '...', 'essay_example': '...'}) liên hệ TRỰC TIẾP tin tức hoặc cổ phiếu hôm nay vào 2 trong 5 môn học của sinh viên: [Quản trị tài chính, Lập dự án đầu tư, Kinh tế vi mô, Nguyên lý kế toán, Hệ thống thông tin kế toán (AIS)]. 'essay_example' phải viết theo văn phong mạch lạc, có thuật ngữ môn học chuẩn xác (ví dụ WACC, NPV, IRR, độ co giãn cung-cầu, Bảng cân đối kế toán, Báo cáo KQKD, chu trình AIS/kiểm soát nội bộ...) để sinh viên có thể nhớ và trích nguyên ý làm ví dụ thi tự luận cuối kỳ.\n"
        "7) 'podcast_script': kịch bản đọc Audio tiếng Việt SÂU SẮC NHƯNG VẪN NHÍ NHẢNH, DÍ DỎM (1.000-1.250 từ, KHÔNG dùng ký tự markdown như ** hay #, viết số thập phân bằng dấu phẩy để đọc tự nhiên). Phải giải thích rõ cơ chế 'tại sao' và 'ảnh hưởng gì về Việt Nam' ở từng tin vĩ mô, từng nhóm cổ phiếu, bài học TA, VÀ kết thúc bằng 1 mục ngắn đọc 2 ví dụ liên hệ môn học thi tự luận cực mượt.\n\n"
        "Trả về ĐÚNG 1 JSON object hợp lệ (không bọc markdown ```json).\n\n"
        f"DỮ LIỆU THẬT:\n{json.dumps(prompt_payload, ensure_ascii=False)}"
    )

    client = genai.Client(api_key=GEMINI_API_KEY, http_options={"api_version": "v1beta", "timeout": 90000})
    seen: set[str] = set()
    last_err: Exception | None = None
    for model_name in GEMINI_FALLBACK_MODELS:
        if model_name in seen:
            continue
        seen.add(model_name)
        try:
            resp = client.models.generate_content(model=model_name, contents=system_prompt)
            raw = (resp.text or "").strip()
            if raw.startswith("```"):
                raw = raw.strip("`").lstrip("json").strip()
            parsed = json.loads(raw)
            parsed["mode"] = f"gemini:{model_name}"
            print(f"[AI] Briefing generated via {model_name}.")
            return parsed
        except Exception as exc:
            print(f"[WARN] Model {model_name} failed ({exc}), trying next fallback...")
            last_err = exc

    raise RuntimeError(f"All Gemini models failed: {last_err}")


def build_daily_briefing(
    market_data: dict[str, Any],
    news: list[dict[str, Any]],
    lesson: dict[str, Any],
    case_stock: dict[str, Any] | None,
) -> dict[str, Any]:
    """Generate briefing & spoken script, using Gemini when available and deterministic engine as fallback."""
    if GEMINI_API_KEY:
        try:
            result = _generate_gemini_briefing(market_data, news, lesson, case_stock)
            if result.get("podcast_script"):
                return result
        except Exception as exc:
            print(f"[WARN] Gemini generation failed, falling back to local tutor engine: {exc}")

    return _generate_local_briefing(market_data, news, lesson, case_stock)
