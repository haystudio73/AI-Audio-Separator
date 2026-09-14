import os
import math
from pathlib import Path
from typing import Dict, Any, Tuple
import soundfile as sf
from pydub.utils import mediainfo
from config import MAX_CONTENT_LENGTH, MAX_AUDIO_DURATION_SECONDS, ALLOWED_EXTENSIONS

def is_allowed_extension(filename: str) -> bool:
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in ALLOWED_EXTENSIONS

def format_duration(seconds: float) -> str:
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins:02d}:{secs:02d}"

def format_size(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"

def get_audio_info(filepath: str | Path) -> Dict[str, Any]:
    """
    Trích xuất metadata và thời lượng audio bằng soundfile hoặc pydub mediainfo.
    """
    filepath = str(filepath)
    file_size = os.path.getsize(filepath)
    duration = None
    samplerate = None
    channels = None
    format_name = None

    # Thử đọc bằng soundfile trước (rất nhanh cho WAV, FLAC, OGG)
    try:
        info = sf.info(filepath)
        duration = info.duration
        samplerate = info.samplerate
        channels = info.channels
        format_name = info.format
    except Exception:
        pass

    # Fallback qua mediainfo (hỗ trợ MP3, M4A, AAC,...)
    if duration is None:
        try:
            info = mediainfo(filepath)
            if "duration" in info and info["duration"]:
                duration = float(info["duration"])
            if "sample_rate" in info and info["sample_rate"]:
                samplerate = int(info["sample_rate"])
            if "channels" in info and info["channels"]:
                channels = int(info["channels"])
            if "format_name" in info and info["format_name"]:
                format_name = str(info["format_name"])
        except Exception as e:
            pass

    # Fallback bằng librosa nếu cần
    if duration is None:
        try:
            import librosa
            duration = float(librosa.get_duration(path=filepath))
        except Exception:
            duration = 0.0

    return {
        "file_size": file_size,
        "file_size_formatted": format_size(file_size),
        "duration_seconds": round(duration or 0.0, 2),
        "duration_formatted": format_duration(duration or 0.0),
        "samplerate": samplerate,
        "channels": channels,
        "format": format_name or Path(filepath).suffix.replace(".", "").upper()
    }

def validate_audio_file(filepath: str | Path) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Xác thực giới hạn dung lượng (<=100MB) và thời lượng (<=8 phút).
    Trả về: (is_valid, error_message, metadata)
    """
    filepath = Path(filepath)
    if not filepath.exists():
        return False, "Tệp âm thanh không tồn tại.", {}

    file_size = os.path.getsize(filepath)
    if file_size > MAX_CONTENT_LENGTH:
        return (
            False,
            f"Dung lượng tệp ({format_size(file_size)}) vượt quá giới hạn cho phép (100 MB).",
            {"file_size": file_size}
        )

    info = get_audio_info(filepath)
    duration = info.get("duration_seconds", 0.0)

    if duration > MAX_AUDIO_DURATION_SECONDS:
        return (
            False,
            f"Thời lượng âm thanh ({info.get('duration_formatted')}) vượt quá giới hạn cho phép (8 phút = 08:00).",
            info
        )

    if duration <= 0:
        return False, "Không thể đọc thời lượng của tệp âm thanh hoặc tệp bị hỏng.", info

    return True, "", info
