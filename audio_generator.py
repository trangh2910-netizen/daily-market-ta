"""Generate Vietnamese podcast audio: Gemini 3.8 Flash TTS (Northern male lively) -> edge-tts -> gTTS."""

from __future__ import annotations

import asyncio
import base64
import re
import tempfile
from pathlib import Path

import edge_tts
from gtts import gTTS

from config import (
    GEMINI_API_KEY,
    GEMINI_TTS_MODEL,
    GEMINI_TTS_STYLE,
    GEMINI_TTS_VOICE,
    TTS_RATE,
    TTS_VOICE,
)


def _clean_for_speech(text: str) -> str:
    cleaned = re.sub(r"[*_`#>]+", "", text)
    cleaned = cleaned.replace("&", " và ").replace("—", ", ").replace("–", ", ")
    cleaned = re.sub(r"\s+\n", "\n", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def _split_chunks(text: str, max_chars: int = 450) -> list[str]:
    """Split script into sentence-aligned chunks so TTS providers never reject long payloads."""
    sentences = re.split(r"(?<=[.!?])\s+|\n+", text)
    chunks: list[str] = []
    current = ""
    for sent in sentences:
        sent = sent.strip()
        if not sent:
            continue
        if len(current) + len(sent) + 1 <= max_chars:
            current = f"{current} {sent}".strip() if current else sent
        else:
            if current:
                chunks.append(current)
            current = sent
    if current:
        chunks.append(current)
    return chunks


def _synthesize_gemini_tts(text: str, out_mp3_path: Path) -> Path:
    """Synthesize expressive Northern Vietnamese male podcast voice using Gemini 3.8 Flash TTS and encode compact MP3."""
    import subprocess
    import imageio_ffmpeg
    from google import genai

    client = genai.Client(api_key=GEMINI_API_KEY, http_options={"api_version": "v1beta", "timeout": 60000})
    interaction = client.interactions.create(
        model=GEMINI_TTS_MODEL,
        input=[
            {
                "type": "user_input",
                "content": [
                    {
                        "type": "text",
                        "text": text,
                        "annotations": [
                            {
                                "type": "speech_metadata",
                                "style": GEMINI_TTS_STYLE,
                            }
                        ],
                    }
                ],
            }
        ],
        response_format={"type": "audio"},
        generation_config={
            "speech_config": [
                {"voice": GEMINI_TTS_VOICE},
            ]
        },
    )
    if not getattr(interaction, "output_audio", None) or not interaction.output_audio.data:
        raise RuntimeError("Gemini TTS returned empty audio payload")

    raw_bytes = base64.b64decode(interaction.output_audio.data)
    wav_tmp = out_mp3_path.with_suffix(".wav")
    wav_tmp.write_bytes(raw_bytes)
    try:
        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        proc = subprocess.run(
            [ffmpeg_exe, "-y", "-i", str(wav_tmp), "-ac", "1", "-c:a", "libmp3lame", "-b:a", "64k", str(out_mp3_path)],
            capture_output=True,
            check=False,
        )
        if proc.returncode == 0 and out_mp3_path.exists() and out_mp3_path.stat().st_size > 1024:
            wav_tmp.unlink(missing_ok=True)
            print(f"[TTS] Generated via {GEMINI_TTS_MODEL} -> compact MP3 (voice={GEMINI_TTS_VOICE}, Northern cheerful style).")
            return out_mp3_path
    except Exception:
        pass

    print(f"[TTS] Generated via {GEMINI_TTS_MODEL} WAV (voice={GEMINI_TTS_VOICE}, Northern cheerful style).")
    return wav_tmp


async def _synthesize_edge_chunked_async(text: str, out_path: Path, voice: str, rate: str) -> None:
    chunks = _split_chunks(text, max_chars=450)
    if not chunks:
        raise ValueError("Empty script text")

    audio_parts: list[bytes] = []
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_root = Path(tmpdir)
        for idx, chunk in enumerate(chunks):
            part_path = tmp_root / f"part_{idx}.mp3"
            last_err: Exception | None = None
            success = False
            for attempt in range(1, 5):
                try:
                    communicate = edge_tts.Communicate(text=chunk, voice=voice, rate=rate)
                    await communicate.save(str(part_path))
                    if part_path.exists() and part_path.stat().st_size > 256:
                        audio_parts.append(part_path.read_bytes())
                        success = True
                        break
                except Exception as exc:
                    last_err = exc
                    await asyncio.sleep(1.5 * attempt)
            if not success:
                raise RuntimeError(f"Chunk {idx} failed: {last_err}")
            await asyncio.sleep(0.8)

    out_path.write_bytes(b"".join(audio_parts))


def generate_podcast_audio(
    script_text: str,
    output_dir: Path,
    voice: str = TTS_VOICE,
    rate: str = TTS_RATE,
) -> Path:
    """Create podcast audio file inside output_dir and return the generated file path (.wav or .mp3)."""
    output_dir.mkdir(parents=True, exist_ok=True)
    clean_text = _clean_for_speech(script_text)

    mp3_path = output_dir / "podcast.mp3"
    if GEMINI_API_KEY:
        try:
            return _synthesize_gemini_tts(clean_text, mp3_path)
        except Exception as exc:
            print(f"[WARN] Gemini TTS unavailable ({exc}); falling back to edge-tts.")
    try:
        asyncio.run(_synthesize_edge_chunked_async(clean_text, mp3_path, voice, rate))
        print(f"[TTS] Generated via edge-tts ({voice}, rate={rate}).")
        return mp3_path
    except Exception as exc:
        print(f"[WARN] edge-tts unavailable ({exc}); switching to gTTS Vietnamese fallback.")

    tts = gTTS(text=clean_text, lang="vi", slow=False)
    tts.save(str(mp3_path))
    print("[TTS] Generated via gTTS (vi).")
    return mp3_path
