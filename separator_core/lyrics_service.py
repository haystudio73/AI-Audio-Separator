"""
Lyrics Extraction Service — powered by OpenAI Whisper (local, no API key needed).

Workflow:
  1. Nhận path file Vocals đã tách (WAV/MP3/FLAC)
  2. Chạy Whisper transcription → list segments [{id, start, end, text}]
  3. Lưu .srt và .lrc vào OUTPUT_FOLDER
  4. Trả về segments JSON cho Frontend Karaoke Editor
"""
import re
import logging
from pathlib import Path
from typing import List, Dict, Any

from config import OUTPUT_FOLDER

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Format helpers
# ---------------------------------------------------------------------------

def _seconds_to_srt_time(seconds: float) -> str:
    """Convert seconds → SRT timestamp: HH:MM:SS,mmm"""
    ms = int(round((seconds % 1) * 1000))
    s  = int(seconds)
    m  = s // 60
    h  = m // 60
    s  = s % 60
    m  = m % 60
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def _seconds_to_lrc_time(seconds: float) -> str:
    """Convert seconds → LRC timestamp: [MM:SS.xx]"""
    cs = int(round((seconds % 1) * 100))
    s  = int(seconds)
    m  = s // 60
    s  = s % 60
    return f"[{m:02d}:{s:02d}.{cs:02d}]"


def _seconds_to_display(seconds: float) -> str:
    """Convert seconds → display MM:SS for editor table"""
    s = int(seconds)
    m = s // 60
    s = s % 60
    return f"{m:02d}:{s:02d}"


def segments_to_srt(segments: List[Dict[str, Any]]) -> str:
    """Convert list of segments to SRT string."""
    lines = []
    for i, seg in enumerate(segments, 1):
        start = _seconds_to_srt_time(seg["start"])
        end   = _seconds_to_srt_time(seg["end"])
        text  = seg["text"].strip()
        lines.append(f"{i}\n{start} --> {end}\n{text}\n")
    return "\n".join(lines)


def segments_to_lrc(segments: List[Dict[str, Any]]) -> str:
    """Convert list of segments to LRC string."""
    lines = []
    for seg in segments:
        ts   = _seconds_to_lrc_time(seg["start"])
        text = seg["text"].strip()
        lines.append(f"{ts}{text}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main extraction function
# ---------------------------------------------------------------------------

def extract_lyrics_from_vocals(
    vocals_path: str | Path,
    whisper_model: str = "base",
    language: str | None = None,
) -> Dict[str, Any]:
    """
    Trích xuất lyrics từ file vocals sử dụng Whisper STT.

    Args:
        vocals_path:   Đường dẫn tới file vocals (WAV/MP3/FLAC).
        whisper_model: Tên Whisper model: tiny | base | small | medium | large.
        language:      Mã ngôn ngữ (vd: 'vi', 'en'). None = auto-detect.

    Returns:
        {
            "success": bool,
            "segments": [{"id", "start", "end", "text", "start_display", "end_display"}],
            "srt_filename": str,
            "lrc_filename": str,
            "detected_language": str,
        }
    """
    vocals_path = Path(vocals_path)
    if not vocals_path.exists():
        raise FileNotFoundError(f"Vocals file not found: {vocals_path}")

    logger.info(f"[Lyrics] Loading Whisper model '{whisper_model}'...")
    try:
        import whisper
    except ImportError:
        raise RuntimeError(
            "openai-whisper is not installed. Please run: pip install openai-whisper"
        )

    model = whisper.load_model(whisper_model)
    logger.info(f"[Lyrics] Transcribing: {vocals_path.name} (lang={language or 'auto'})")

    transcribe_kwargs: Dict[str, Any] = {
        "verbose": False,
        "word_timestamps": False,
    }
    if language:
        transcribe_kwargs["language"] = language

    result = model.transcribe(str(vocals_path), **transcribe_kwargs)

    raw_segments = result.get("segments", [])
    detected_lang = result.get("language", "unknown")
    logger.info(f"[Lyrics] Got {len(raw_segments)} segments. Detected lang: {detected_lang}")

    # Build normalized segment list
    segments = []
    for i, seg in enumerate(raw_segments):
        text = seg.get("text", "").strip()
        if not text:
            continue
        segments.append({
            "id":            i + 1,
            "start":         round(seg["start"], 3),
            "end":           round(seg["end"],   3),
            "text":          text,
            "start_display": _seconds_to_display(seg["start"]),
            "end_display":   _seconds_to_display(seg["end"]),
        })

    # Build output filenames
    base_name = re.sub(r"\.[^.]+$", "", vocals_path.name)
    srt_filename = f"{base_name}_lyrics.srt"
    lrc_filename = f"{base_name}_lyrics.lrc"

    srt_path = OUTPUT_FOLDER / srt_filename
    lrc_path = OUTPUT_FOLDER / lrc_filename

    srt_path.write_text(segments_to_srt(segments), encoding="utf-8")
    lrc_path.write_text(segments_to_lrc(segments), encoding="utf-8")
    logger.info(f"[Lyrics] Saved: {srt_filename}, {lrc_filename}")

    return {
        "success":           True,
        "segments":          segments,
        "srt_filename":      srt_filename,
        "lrc_filename":      lrc_filename,
        "detected_language": detected_lang,
        "total_lines":       len(segments),
    }


# ---------------------------------------------------------------------------
# Utility: re-save edited segments from UI
# ---------------------------------------------------------------------------

def save_edited_lyrics(
    segments: List[Dict[str, Any]],
    base_filename: str,
) -> Dict[str, str]:
    """
    Lưu lại segments đã được user chỉnh sửa ra file SRT và LRC.

    Args:
        segments:      List segments sau khi edit [{id, start, end, text}]
        base_filename: Tên file vocals gốc (dùng để đặt tên output).

    Returns:
        {"srt_filename": str, "lrc_filename": str}
    """
    base_name = re.sub(r"\.[^.]+$", "", base_filename)
    srt_filename = f"{base_name}_lyrics.srt"
    lrc_filename = f"{base_name}_lyrics.lrc"

    (OUTPUT_FOLDER / srt_filename).write_text(segments_to_srt(segments), encoding="utf-8")
    (OUTPUT_FOLDER / lrc_filename).write_text(segments_to_lrc(segments), encoding="utf-8")
    logger.info(f"[Lyrics] Re-saved edited lyrics: {srt_filename}, {lrc_filename}")

    return {"srt_filename": srt_filename, "lrc_filename": lrc_filename}
