import os
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from config import MODEL_FOLDER

logger = logging.getLogger(__name__)

CURATED_MODELS = [
    {
        "id": "mel_band_roformer_kim_ft3_unwa.ckpt",
        "name": "Mel-Band RoFormer Kim | FT 3 (Unwa)",
        "architecture": "Mel-Band RoFormer",
        "stems": ["Vocals", "Instrumental"],
        "target_stems": 2,
        "recommended_hardware": "GPU (CUDA)",
        "size_mb": 640,
        "sdr": "12.5 - 14.0 dB",
        "description_vi": "Đỉnh cao chất lượng phòng thu (Studio Quality). Tách sạch âm hơi, sibilants và loại bỏ triệt để rò rỉ âm sắc.",
        "description_en": "Studio quality state-of-the-art model. Preserves micro-harmonics, breathy vocals, zero bleed-through.",
        "badge": "Top Quality / Best SDR"
    },
    {
        "id": "UVR-MDX-NET-Inst_HQ_3.onnx",
        "name": "UVR-MDX-NET Inst HQ 3",
        "architecture": "Dual-Stream TFC-TDF U-Net (ONNX)",
        "stems": ["Vocals", "Instrumental"],
        "target_stems": 2,
        "recommended_hardware": "CPU hoặc GPU",
        "size_mb": 64,
        "sdr": "11.1 - 12.0 dB",
        "description_vi": "Siêu nhanh, dung lượng nhỏ (<70MB), tiêu thụ <4GB RAM. Lý tưởng tạo beat Karaoke sạch hoàn toàn trên CPU.",
        "description_en": "Ultra-fast, lightweight (<70MB), <4GB RAM. Perfect for crisp Karaoke instrumental on CPU.",
        "badge": "Ultra Fast / CPU Friendly"
    },
    {
        "id": "model_bs_roformer_ep_317_sdr_12.9755.ckpt",
        "name": "BS-RoFormer (Viperx 1297)",
        "architecture": "Band-Split RoFormer",
        "stems": ["Vocals", "Instrumental"],
        "target_stems": 2,
        "recommended_hardware": "GPU / CPU",
        "size_mb": 640,
        "sdr": "10.7 - 14.5 dB",
        "description_vi": "Mô hình Band-Split kinh điển của Viperx/MVSep, độ chi tiết giọng hát xuất sắc ở dải trung âm.",
        "description_en": "Classic Band-Split architecture by Viperx, exceptional vocal clarity in mid-range frequencies.",
        "badge": "Viperx Classic"
    },
    {
        "id": "htdemucs.yaml",
        "name": "HT-Demucs v4 (Meta AI)",
        "architecture": "Hybrid Transformer Demucs",
        "stems": ["Vocals", "Drums", "Bass", "Other"],
        "target_stems": 4,
        "recommended_hardware": "GPU / CPU",
        "size_mb": 316,
        "sdr": "9.2 - 11.5 dB",
        "description_vi": "Phân tách thành 4 track độc lập: Vocals, Drums (Trống), Bass (Âm trầm) và Other (Nhạc cụ khác).",
        "description_en": "Separates into 4 stems: Vocals, Drums, Bass, and Other. High overall balance.",
        "badge": "4 Stems Isolation"
    },
    {
        "id": "melband_roformer_big_beta4.ckpt",
        "name": "Mel-Band RoFormer Big Beta 4 (Unwa)",
        "architecture": "Mel-Band RoFormer (Expanded)",
        "stems": ["Vocals", "Instrumental"],
        "target_stems": 2,
        "recommended_hardware": "GPU (>= 8GB VRAM)",
        "size_mb": 1570,
        "sdr": "12.5 - 14.2 dB",
        "description_vi": "Phiên bản mở rộng kích thước mô hình, đạt độ tách bạch âm thanh phòng thu tối đa cho việc sampling/remix.",
        "description_en": "Expanded model parameters for maximum acoustic separation. Requires powerful GPU.",
        "badge": "Maximum Separation"
    },
    {
        "id": "dereverb_mel_band_roformer_anvuew_sdr_19.1729.ckpt",
        "name": "Dereverb Mel-Band RoFormer (Anvuew)",
        "architecture": "BS-RoFormer De-reverb",
        "stems": ["Dry Vocals", "Reverb Tail"],
        "target_stems": 2,
        "recommended_hardware": "GPU / CPU",
        "size_mb": 640,
        "sdr": "De-reverb / Clean",
        "description_vi": "Khử tiếng vang phòng thu và tiếng vọng, làm sạch vocal trước khi xử lý ngôn ngữ hoặc luyện giọng RVC.",
        "description_en": "Removes studio reverb, echo and reflections for clean speech/vocal preprocessing.",
        "badge": "De-Reverb Vocal"
    }
]

def is_model_downloaded(model_filename: str) -> bool:
    """Kiểm tra tệp model đã tồn tại trong thư mục cache chưa.
    
    Xử lý đặc biệt cho Demucs: file .yaml config chỉ ~21 bytes nên không
    dùng ngưỡng 1024 bytes. Thay vào đó kiểm tra xem có file .th trọng số đi kèm không.
    """
    target = MODEL_FOLDER / model_filename
    ext = Path(model_filename).suffix.lower()

    # ── Demucs / YAML config: file nhỏ, kiểm tra theo file .th đi kèm ────────
    if ext == ".yaml":
        if not target.exists():
            return False
        # Kiểm tra có ít nhất một file .th trọng số trong thư mục models
        th_files = list(MODEL_FOLDER.glob("*.th"))
        return len(th_files) > 0

    # ── Model thông thường: file lớn hơn 1KB ──────────────────────────────────
    if target.exists() and target.stat().st_size > 1024:
        return True

    # Glob fallback: .ckpt / .onnx / .pt với tên tương tự
    for f in MODEL_FOLDER.glob(f"*{Path(model_filename).stem}*"):
        if f.is_file() and f.stat().st_size > 1024:
            return True

    return False


def get_models_list() -> List[Dict[str, Any]]:
    """Lấy danh sách mô hình kèm trạng thái đã tải hay chưa"""
    models = []
    for m in CURATED_MODELS:
        m_copy = dict(m)
        m_copy["is_downloaded"] = is_model_downloaded(m["id"])
        models.append(m_copy)
    return models


def download_model_if_needed(model_filename: str) -> bool:
    """
    Tự động tải mô hình nếu chưa tồn tại.
    Sử dụng Separator.download_model_files từ audio-separator.
    
    Lưu ý: download_model_files() trả về tuple, không phải bool.
    Sau khi download, thử load_model để xác nhận model hoạt động.
    """
    if is_model_downloaded(model_filename):
        logger.info(f"Model {model_filename} already exists in {MODEL_FOLDER}")
        return True

    logger.info(f"Downloading model {model_filename} into {MODEL_FOLDER}...")
    try:
        from audio_separator.separator import Separator
        sep = Separator(
            model_file_dir=str(MODEL_FOLDER),
            log_level=logging.INFO
        )
        # download_model_files trả về tuple (filename, arch, friendly_name, path, ...)
        # không phải bool, nên kiểm tra sau bằng is_model_downloaded
        sep.download_model_files(model_filename)

        # Với Demucs YAML: download_model_files đã tải đủ file .th + .yaml,
        # dùng load_model để xác nhận rồi trả về True
        if Path(model_filename).suffix.lower() == ".yaml":
            try:
                sep.load_model(model_filename)
                logger.info(f"Demucs model {model_filename} verified via load_model.")
                return True
            except Exception as verify_err:
                logger.warning(f"Demucs load_model verify failed: {verify_err}")
                # Vẫn có thể dùng được nếu file tồn tại
                return is_model_downloaded(model_filename)

        return is_model_downloaded(model_filename)

    except Exception as e:
        logger.error(f"Error downloading model {model_filename}: {e}")
        # Thử fallback qua load_model
        try:
            from audio_separator.separator import Separator
            sep = Separator(
                model_file_dir=str(MODEL_FOLDER),
                log_level=logging.INFO
            )
            sep.load_model(model_filename)
            return True
        except Exception as e2:
            logger.error(f"Fallback load_model failed for {model_filename}: {e2}")
            return False
