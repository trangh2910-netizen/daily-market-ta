"""Generate a 9:16 (1080x1920) vertical TikTok/Shorts video with zoom motion and synced Vietnamese captions."""

from __future__ import annotations

import json
import re
import subprocess
import tempfile
import wave
from pathlib import Path
from typing import Any

import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

from audio_generator import generate_podcast_audio
from config import GEMINI_API_KEY, GEMINI_FALLBACK_MODELS

WIDTH = 1080
HEIGHT = 1920
FPS = 24


def _find_font(bold: bool = False) -> str | None:
    candidates = (
        [
            "C:/Windows/Fonts/arialbd.ttf",
            "C:/Windows/Fonts/segoeuib.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ]
        if bold
        else [
            "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/segoeui.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]
    )
    for path in candidates:
        if Path(path).exists():
            return path
    return None


def _load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    font_path = _find_font(bold=bold)
    if font_path:
        return ImageFont.truetype(font_path, size=size)
    return ImageFont.load_default()


def build_tiktok_script(context: dict[str, Any]) -> str:
    """Create a punchy 45-60s TikTok script (~135-165 words) grounded strictly in today's real JSON."""
    vni = context["vnindex"]
    lesson = context["lesson"]
    case_stock = context.get("case_stock")
    macro = context.get("macro", [])
    news = context.get("news", [])

    if GEMINI_API_KEY:
        try:
            from google import genai

            payload = {
                "today_vn": context["generated_date_vn"],
                "trade_date_vn": context["market_trade_date_vn"],
                "vnindex": {"close": vni["close"], "change_pct": vni["change_pct"], "rsi14": vni["rsi14"]},
                "macro": macro[:3],
                "top_news": [{"title": n["title"], "summary": n["summary"]} for n in news[:2]],
                "lesson": {"id": lesson["id"], "title": lesson["title"], "concept_plain": lesson["concept_plain"]},
                "case_stock": {
                    "symbol": case_stock["symbol"],
                    "close": case_stock["close"],
                    "change_pct": case_stock["change_pct"],
                    "candle": case_stock["candle"],
                    "vol_ratio": case_stock["vol_ratio"],
                }
                if case_stock
                else None,
            }
            prompt = (
                "Bạn là nam TikToker tài chính miền Bắc DÍ DỎM, NHÍ NHẢNH, nói cực nhanh gọn.\n"
                "Dựa 100% vào JSON thật dưới đây (không bịa số), viết ĐÚNG 1 bản cập nhật ngắn gọn 80-100 từ (đọc khoảng 30-35 giây):\n"
                "- Câu 1 (Hook 3s): Tin nóng nhất hoặc con số giật gân nhất hôm nay.\n"
                "- 2 câu giữa: Điểm cực nhanh vĩ mô + VN-Index và điểm nhấn trên biểu đồ mã minh họa (không giảng lý thuyết dài dòng, không khuyến nghị mua bán).\n"
                "- Câu cuối: Follow để cập nhật nhanh mỗi ngày!\n"
                "CHỈ trả về văn bản thuần tiếng Việt để đọc thành tiếng (không markdown, không emoji, viết số thập phân bằng dấu phẩy).\n\n"
                f"JSON:\n{json.dumps(payload, ensure_ascii=False)}"
            )
            client = genai.Client(api_key=GEMINI_API_KEY, http_options={"api_version": "v1beta", "timeout": 45000})
            for model_name in GEMINI_FALLBACK_MODELS:
                try:
                    resp = client.models.generate_content(model=model_name, contents=prompt)
                    txt = re.sub(r"[*_`#>]+", "", (resp.text or "").strip())
                    if len(txt.split()) >= 45:
                        print(f"[TIKTOK] Script written via {model_name}.")
                        return txt
                except Exception:
                    continue
        except Exception as exc:
            print(f"[WARN] Gemini TikTok script failed ({exc}), using local TikTok script.")

    sym = case_stock["symbol"] if case_stock else "VN-Index"
    sym_chg = case_stock["change_pct"] if case_stock else vni["change_pct"]
    return (
        f"Alo, cập nhật nhanh 30 giây! Vàng thế giới vừa giảm hơn 4 phẩy 6 phần trăm, chứng khoán Mỹ cũng đỏ lửa. "
        f"Ở Việt Nam, VN-Index tạm đứng ở {vni['close']:.2f} điểm ngay sát hỗ trợ 1675 điểm. "
        f"Điểm nhấn biểu đồ hôm nay là mã {sym} biến động {sym_chg:+.2f} phần trăm, minh họa cho {lesson['title']}. "
        f"Follow kênh để cập nhật nhanh thị trường mỗi ngày nhé!"
    )


def _get_audio_duration_seconds(audio_path: Path) -> float:
    if audio_path.suffix.lower() == ".wav":
        with wave.open(str(audio_path), "rb") as wf:
            return wf.getnframes() / float(wf.getframerate())

    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    proc = subprocess.run(
        [ffmpeg_exe, "-i", str(audio_path)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="ignore",
    )
    m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", proc.stderr)
    if m:
        h, mins, secs = int(m.group(1)), int(m.group(2)), float(m.group(3))
        return h * 3600 + mins * 60 + secs
    return 45.0


def _split_captions(script: str, total_dur: float) -> list[tuple[float, float, str]]:
    """Split script into readable short caption cards proportional to character count."""
    raw_sentences = re.split(r"(?<=[.!?])\s+", script.strip())
    chunks: list[str] = []
    for sent in raw_sentences:
        words = sent.split()
        while len(words) > 13:
            chunks.append(" ".join(words[:11]))
            words = words[11:]
        if words:
            chunks.append(" ".join(words))

    if not chunks:
        return [(0.0, total_dur, script)]

    weights = [max(len(c), 8) for c in chunks]
    total_weight = sum(weights)
    timeline: list[tuple[float, float, str]] = []
    cur = 0.0
    for c, w in zip(chunks, weights):
        dur = (w / total_weight) * total_dur
        timeline.append((cur, cur + dur, c))
        cur += dur
    return timeline


def _wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, max_width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    cur = ""
    for w in words:
        test = f"{cur} {w}".strip()
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] <= max_width:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def _crop_zoom_chart(chart_img: Image.Image, zoom: float, target_w: int, target_h: int) -> Image.Image:
    cw, ch = chart_img.size
    crop_w = int(cw / zoom)
    crop_h = int(ch / zoom)
    # Bias crop slightly toward the right side where the latest candle sits
    left = max(0, int((cw - crop_w) * 0.72))
    top = max(0, int((ch - crop_h) * 0.35))
    cropped = chart_img.crop((left, top, left + crop_w, top + crop_h))
    return cropped.resize((target_w, target_h), Image.Resampling.LANCZOS)


def render_tiktok_video(context: dict[str, Any], ep_dir: Path, out_mp4_path: Path) -> Path:
    """Render 1080x1920 vertical MP4 video combining zoomed TA charts, captions, and lively voice."""
    script = build_tiktok_script(context)
    with tempfile.TemporaryDirectory() as tmpdir:
        audio_path = generate_podcast_audio(script, Path(tmpdir))
        return _render_video_from_audio(context, ep_dir, out_mp4_path, script, audio_path)


def _render_video_from_audio(
    context: dict[str, Any],
    ep_dir: Path,
    out_mp4_path: Path,
    script: str,
    audio_path: Path,
) -> Path:
    duration = _get_audio_duration_seconds(audio_path)

    vni_chart_path = ep_dir / "vnindex.png"
    lesson_chart_path = ep_dir / "lesson_chart.png"
    img_vni = Image.open(vni_chart_path).convert("RGB")
    img_lesson = Image.open(lesson_chart_path if lesson_chart_path.exists() else vni_chart_path).convert("RGB")

    # Pre-fit chart canvas dimensions
    chart_box_w, chart_box_h = 1000, 620
    img_vni_base = img_vni.resize((chart_box_w, chart_box_h), Image.Resampling.LANCZOS)
    img_lesson_base = img_lesson.resize((chart_box_w, chart_box_h), Image.Resampling.LANCZOS)

    font_tag = _load_font(34, bold=True)
    font_title = _load_font(44, bold=True)
    font_sub = _load_font(30, bold=False)
    font_cap = _load_font(54, bold=True)
    font_disc = _load_font(25, bold=False)

    captions = _split_captions(script, duration)
    total_frames = max(1, int(duration * FPS))

    lesson = context["lesson"]
    sym = context.get("case_stock_symbol") or "VNINDEX"
    header_badge = f"HỌC ĐỌC BIỂU ĐỒ F0 · TẬP {lesson['id']}"
    header_sub = f"Ngày {context['generated_date_vn']} | Minh họa: {sym}"

    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    out_mp4_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        ffmpeg_exe,
        "-y",
        "-f",
        "rawvideo",
        "-vcodec",
        "rawvideo",
        "-pix_fmt",
        "rgb24",
        "-s",
        f"{WIDTH}x{HEIGHT}",
        "-r",
        str(FPS),
        "-i",
        "-",
        "-i",
        str(audio_path),
        "-c:v",
        "libx264",
        "-preset",
        "fast",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-movflags",
        "+faststart",
        "-shortest",
        str(out_mp4_path),
    ]

    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    assert proc.stdin is not None

    cap_idx = 0
    for f_idx in range(total_frames):
        t = f_idx / float(FPS)
        progress = min(1.0, t / max(duration, 0.1))

        canvas = Image.new("RGB", (WIDTH, HEIGHT), (11, 17, 32))
        draw = ImageDraw.Draw(canvas)

        # Header badge & title
        draw.rounded_rectangle([(60, 75), (650, 140)], radius=22, fill=(2, 132, 199))
        draw.text((88, 89), header_badge, font=font_tag, fill=(255, 255, 255))
        draw.text((60, 160), header_sub, font=font_sub, fill=(148, 163, 184))

        lesson_short = lesson["title"].split(":", 1)[-1].strip()
        title_lines = _wrap_text(draw, lesson_short, font_title, 960)[:2]
        ty = 212
        for line in title_lines:
            draw.text((60, ty), line, font=font_title, fill=(125, 211, 252))
            ty += 52

        # Switch chart from VN-Index (first 38% of video) to Today's TA Lesson chart (remaining 62%)
        use_lesson_chart = progress >= 0.38
        active_img = img_lesson_base if use_lesson_chart else img_vni_base
        local_prog = (progress - 0.38) / 0.62 if use_lesson_chart else progress / 0.38
        zoom = 1.0 + 0.14 * min(1.0, max(0.0, local_prog))
        chart_frame = _crop_zoom_chart(active_img, zoom, chart_box_w, chart_box_h)

        chart_y = 355
        draw.rounded_rectangle([(36, chart_y - 4), (1044, chart_y + chart_box_h + 4)], radius=18, outline=(56, 189, 248), width=3)
        canvas.paste(chart_frame, (40, chart_y))

        # Active caption lookup
        while cap_idx + 1 < len(captions) and t >= captions[cap_idx][1]:
            cap_idx += 1
        cap_text = captions[cap_idx][2]

        # Caption box in lower half
        cap_box_top = 1045
        draw.rounded_rectangle([(48, cap_box_top), (1032, 1520)], radius=28, fill=(17, 24, 39), outline=(51, 65, 85), width=2)
        cap_lines = _wrap_text(draw, cap_text, font_cap, 900)[:5]
        cy = cap_box_top + max(45, (475 - len(cap_lines) * 74) // 2)
        for line in cap_lines:
            bbox = draw.textbbox((0, 0), line, font=font_cap)
            lw = bbox[2] - bbox[0]
            lx = (WIDTH - lw) // 2
            draw.text((lx + 3, cy + 3), line, font=font_cap, fill=(0, 0, 0))
            draw.text((lx, cy), line, font=font_cap, fill=(250, 204, 21))
            cy += 74

        # Progress bar
        bar_y = 1580
        draw.rounded_rectangle([(60, bar_y), (1020, bar_y + 14)], radius=7, fill=(30, 41, 59))
        fill_x = max(74, 60 + int(960 * progress))
        draw.rounded_rectangle([(60, bar_y), (fill_x, bar_y + 14)], radius=7, fill=(56, 189, 248))

        # Disclaimer footer
        disc = "Chia sẻ kiến thức Phân tích kỹ thuật – Không phải khuyến nghị đầu tư"
        dbbox = draw.textbbox((0, 0), disc, font=font_disc)
        draw.text(((WIDTH - (dbbox[2] - dbbox[0])) // 2, 1785), disc, font=font_disc, fill=(148, 163, 184))

        proc.stdin.write(canvas.tobytes())

    proc.stdin.close()
    stderr_out = proc.stderr.read().decode("utf-8", errors="ignore") if proc.stderr else ""
    ret = proc.wait()
    if ret != 0:
        raise RuntimeError(f"ffmpeg failed ({ret}): {stderr_out[-500:]}")

    print(f"[TIKTOK] Rendered 9:16 video ({duration:.1f}s) -> {out_mp4_path}")
    return out_mp4_path
