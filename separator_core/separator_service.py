import os
import time
import logging
import threading
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
import torch

from config import OUTPUT_FOLDER, MODEL_FOLDER, IS_CUDA_AVAILABLE, NUMBA_CACHE_DIR
from separator_core.audio_utils import get_audio_info, format_size
from separator_core.model_manager import download_model_if_needed

# Ensure Numba cache directory is always set before any audio libraries load
os.environ.setdefault("NUMBA_CACHE_DIR", str(NUMBA_CACHE_DIR))

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Model Cache — tải model 1 lần, tái sử dụng cho mọi request
# ---------------------------------------------------------------------------
_cache_lock = threading.Lock()

_cached_separator   = None          # Separator instance đang giữ model
_cached_model_key: Optional[str] = None   # "model_checkpoint|device|format"


def _make_cache_key(model_checkpoint: str, device_mode: str, output_format: str) -> str:
    return f"{model_checkpoint}|{device_mode}|{output_format.upper()}"


def _build_mdxc_config(segment_size: int, overlap: int, batch_size: int) -> dict:
    return {
        "segment_size": int(segment_size),
        "overlap": int(overlap),
        "batch_size": int(batch_size),
        "override_model_segment_size": False,
        "pitch_shift": 0,
    }


def _load_separator(
    model_checkpoint: str,
    device_mode: str,
    output_format: str,
    segment_size: int,
    overlap: int,
    batch_size: int,
    use_autocast: bool,
):
    """Khởi tạo và load Separator mới (chỉ gọi khi cần)."""
    from audio_separator.separator import Separator

    is_gpu = (device_mode.lower() == "cuda") and IS_CUDA_AVAILABLE
    torch_device = torch.device("cuda" if is_gpu else "cpu")

    mdxc_config = _build_mdxc_config(segment_size, overlap, batch_size)

    separator = Separator(
        log_level=logging.INFO,
        model_file_dir=str(MODEL_FOLDER),
        output_dir=str(OUTPUT_FOLDER),
        output_format=output_format.upper(),
        use_autocast=is_gpu and use_autocast,
        mdxc_params=mdxc_config,
    )

    # Ghi đè torch_device bằng torch.device object (audio-separator yêu cầu)
    separator.torch_device = torch_device
    if is_gpu:
        separator.onnx_execution_provider = ["CUDAExecutionProvider"]
    else:
        separator.onnx_execution_provider = ["CPUExecutionProvider"]

    # Đồng bộ arch_specific_params
    if hasattr(separator, "arch_specific_params") and "MDXC" in separator.arch_specific_params:
        separator.arch_specific_params["MDXC"] = mdxc_config

    logger.info(f"Loading model: {model_checkpoint} onto {torch_device}")
    separator.load_model(model_filename=model_checkpoint)
    logger.info(f"Model {model_checkpoint} loaded and cached on {torch_device}")

    return separator


def _get_separator(
    model_checkpoint: str,
    device_mode: str,
    output_format: str,
    segment_size: int,
    overlap: int,
    batch_size: int,
    use_autocast: bool,
):
    """
    Trả về Separator đã được cache (tải mới nếu model/device/format thay đổi).
    Thread-safe nhờ _cache_lock.
    """
    global _cached_separator, _cached_model_key

    cache_key = _make_cache_key(model_checkpoint, device_mode, output_format)

    with _cache_lock:
        if _cached_separator is None or _cached_model_key != cache_key:
            if _cached_separator is not None:
                logger.info(
                    f"Model config changed ({_cached_model_key} → {cache_key}), reloading..."
                )
                # Giải phóng bộ nhớ GPU cũ trước khi tải model mới
                try:
                    del _cached_separator
                    if torch.cuda.is_available():
                        torch.cuda.empty_cache()
                except Exception:
                    pass

            # Đảm bảo model file đã có trước khi load
            download_model_if_needed(model_checkpoint)

            _cached_separator = _load_separator(
                model_checkpoint=model_checkpoint,
                device_mode=device_mode,
                output_format=output_format,
                segment_size=segment_size,
                overlap=overlap,
                batch_size=batch_size,
                use_autocast=use_autocast,
            )
            _cached_model_key = cache_key
        else:
            logger.info(
                f"Reusing cached model: {model_checkpoint} on {device_mode.upper()}"
            )
            # Cập nhật output_dir và output_format nếu cần (không cần reload model)
            _cached_separator.output_dir = str(OUTPUT_FOLDER)

    return _cached_separator


def invalidate_model_cache():
    """Xóa cache model (gọi khi user đổi model/settings)."""
    global _cached_separator, _cached_model_key
    with _cache_lock:
        if _cached_separator is not None:
            logger.info("Invalidating model cache...")
            try:
                del _cached_separator
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
            except Exception:
                pass
            _cached_separator = None
            _cached_model_key = None


def get_cache_status() -> Dict[str, Any]:
    """Trả về trạng thái cache hiện tại để hiển thị trên UI."""
    with _cache_lock:
        if _cached_separator is not None and _cached_model_key is not None:
            parts = _cached_model_key.split("|")
            return {
                "loaded": True,
                "model": parts[0] if len(parts) > 0 else "?",
                "device": parts[1] if len(parts) > 1 else "?",
                "format": parts[2] if len(parts) > 2 else "?",
            }
        return {"loaded": False}


# ---------------------------------------------------------------------------
# Main separation function
# ---------------------------------------------------------------------------

def _is_demucs_model(model_checkpoint: str) -> bool:
    """Trả về True nếu model là Demucs config (.yaml) → dùng demucs library trực tiếp."""
    return Path(model_checkpoint).suffix.lower() == ".yaml"


def process_stem_separation(
    input_audio_file: str | Path,
    model_checkpoint: str = "mel_band_roformer_kim_ft3_unwa.ckpt",
    device_mode: str = "cuda",
    output_format: str = "WAV",
    segment_size: int = 256,
    overlap: int = 4,
    batch_size: int = 1,
    use_autocast: bool = True
) -> Dict[str, Any]:
    """
    Thực hiện phân tách nguồn âm nhạc (MSS).
    - Nếu model là .yaml (Demucs): dùng demucs library trực tiếp (Method 1).
    - Các model còn lại: dùng audio-separator pipeline (có cache).
    """
    # ── Demucs native routing ────────────────────────────────────────────────
    if _is_demucs_model(model_checkpoint):
        logger.info(f"[Router] Model {model_checkpoint} is Demucs → using demucs_service")
        from separator_core.demucs_service import process_demucs_separation
        return process_demucs_separation(
            input_audio_file=input_audio_file,
            model_filename=model_checkpoint,
            device_mode=device_mode,
            output_format=output_format,
        )
    # ── audio-separator pipeline ─────────────────────────────────────────────

    start_time = time.time()
    input_audio_file = Path(input_audio_file)
    if not input_audio_file.exists():
        raise FileNotFoundError(f"Input audio file not found: {input_audio_file}")

    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    os.makedirs(MODEL_FOLDER, exist_ok=True)

    # Lấy Separator từ cache (hoặc load mới nếu chưa có)
    separator = _get_separator(
        model_checkpoint=model_checkpoint,
        device_mode=device_mode,
        output_format=output_format,
        segment_size=segment_size,
        overlap=overlap,
        batch_size=batch_size,
        use_autocast=use_autocast,
    )

    # Bóc tách âm thanh (phần này mới tốn thời gian thực sự)
    logger.info(f"Starting separation for {input_audio_file.name}...")
    output_files = separator.separate(str(input_audio_file))
    elapsed_time = round(time.time() - start_time, 2)

    logger.info(f"Separation completed in {elapsed_time}s. Generated files: {output_files}")

    # Chuẩn bị danh sách stems đầu ra
    stems = []
    for stem_path_str in output_files:
        p = Path(stem_path_str)
        if not p.is_absolute():
            p = OUTPUT_FOLDER / p

        if p.exists():
            stem_info = get_audio_info(p)
            stem_name = "Output"
            lower_name = p.name.lower()
            if "vocal" in lower_name:
                stem_name = "Vocals"
            elif "inst" in lower_name:
                stem_name = "Instrumental"
            elif "drum" in lower_name:
                stem_name = "Drums"
            elif "bass" in lower_name:
                stem_name = "Bass"
            elif "other" in lower_name:
                stem_name = "Other"
            elif "reverb" in lower_name:
                stem_name = "Reverb Tail"
            elif "dry" in lower_name or "dereverb" in lower_name:
                stem_name = "Dry Vocals"

            stems.append({
                "stem_name": stem_name,
                "filename": p.name,
                "download_url": f"/api/audio/outputs/{p.name}",
                "file_size": stem_info.get("file_size", 0),
                "file_size_formatted": stem_info.get("file_size_formatted", "0 B"),
                "duration_seconds": stem_info.get("duration_seconds", 0.0),
                "duration_formatted": stem_info.get("duration_formatted", "00:00"),
                "format": stem_info.get("format", output_format)
            })

    return {
        "success": True,
        "input_filename": input_audio_file.name,
        "model_used": model_checkpoint,
        "device_used": str(separator.torch_device),
        "processing_time_seconds": elapsed_time,
        "stems": stems
    }
