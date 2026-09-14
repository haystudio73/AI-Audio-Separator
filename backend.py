import os
import uuid
import time
import logging
import threading
from datetime import datetime
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory, abort, make_response
from werkzeug.utils import secure_filename
import torch

from config import (
    UPLOAD_FOLDER, OUTPUT_FOLDER, MODEL_FOLDER, AGENT_DIR,
    MAX_CONTENT_LENGTH, MAX_AUDIO_DURATION_SECONDS,
    IS_CUDA_AVAILABLE, DEFAULT_DEVICE
)
from separator_core.audio_utils import is_allowed_extension, validate_audio_file, format_size
from separator_core.history_manager import get_history, add_history_entry, delete_history_entry, clear_history
from separator_core.model_manager import get_models_list, download_model_if_needed
from separator_core.separator_service import process_stem_separation, invalidate_model_cache, get_cache_status
from separator_core.settings_service import get_settings, save_settings
from separator_core.job_manager import (
    create_job, update_job_phase, update_job_progress,
    complete_job, fail_job, get_job,
    request_cancel, is_cancel_requested, cancel_job,
    set_job_thread_id
)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - [BACKEND] - %(levelname)s - %(message)s")
logger = logging.getLogger("backend")

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH

# Enable CORS for Frontend communication (Port 3000 -> Port 5000)
@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = make_response()
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With"
        response.headers["Access-Control-Max-Age"] = "86400"
        return response, 204

@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With"
    return response

def append_agent_action_log(action_name: str, details: dict):
    """Tự động ghi nhận nhật ký hành động vào thư mục .agent/walkthrough.md"""
    try:
        wt_file = AGENT_DIR / "walkthrough.md"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"\n### [{timestamp}] {action_name}\n"
        for k, v in details.items():
            log_entry += f"- **{k}**: {v}\n"
        with open(wt_file, "a", encoding="utf-8") as f:
            f.write(log_entry)
    except Exception as e:
        logger.error(f"Failed to write to .agent/walkthrough.md: {e}")

@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({
        "success": False,
        "error": "Dung lượng tệp vượt quá giới hạn 100 MB cho phép.",
        "error_en": "File size exceeds the allowed 100 MB limit."
    }), 413

@app.route("/")
@app.route("/api/health")
def api_health():
    """Health check & API descriptor endpoint"""
    return jsonify({
        "status": "online",
        "service": "AI Music Source Separation Backend API",
        "port": int(os.environ.get("PORT", 5000)),
        "cuda_available": IS_CUDA_AVAILABLE,
        "device": DEFAULT_DEVICE,
        "version": "1.0.0"
    })

@app.route("/api/system_info", methods=["GET"])
def system_info():
    gpu_name = torch.cuda.get_device_name(0) if IS_CUDA_AVAILABLE else "None"
    vram_total = None
    vram_free = None
    if IS_CUDA_AVAILABLE:
        try:
            free, total = torch.cuda.mem_get_info()
            vram_total = f"{total / (1024**3):.1f} GB"
            vram_free = f"{free / (1024**3):.1f} GB"
        except Exception:
            pass

    return jsonify({
        "cuda_available": IS_CUDA_AVAILABLE,
        "device_name": gpu_name,
        "vram_total": vram_total,
        "vram_free": vram_free,
        "default_device": DEFAULT_DEVICE,
        "cpu_threads": os.cpu_count() or 4
    })

@app.route("/api/models", methods=["GET"])
def list_models():
    models = get_models_list()
    return jsonify({"success": True, "models": models})

@app.route("/api/models/download", methods=["POST"])
def download_model():
    data = request.get_json() or {}
    model_filename = data.get("model_filename")
    if not model_filename:
        return jsonify({"success": False, "error": "Thiếu model_filename"}), 400

    success = download_model_if_needed(model_filename)
    if success:
        append_agent_action_log("Tải Model Thành Công", {"Model": model_filename})
        return jsonify({"success": True, "message": f"Mô hình {model_filename} đã sẵn sàng."})
    return jsonify({"success": False, "error": f"Không thể tải mô hình {model_filename}."}), 500

@app.route("/api/settings", methods=["GET", "POST"])
def manage_settings():
    if request.method == "GET":
        return jsonify({"success": True, "settings": get_settings()})
    
    new_data = request.get_json() or {}
    updated = save_settings(new_data)
    # Xóa model cache để load lại với settings mới
    invalidate_model_cache()
    append_agent_action_log("Cập Nhật Cài Đặt", new_data)
    return jsonify({"success": True, "settings": updated})

@app.route("/api/upload", methods=["POST"])
def upload_audio():
    if "audio_file" not in request.files:
        return jsonify({
            "success": False,
            "error": "Không tìm thấy tệp tải lên.",
            "error_en": "No file uploaded."
        }), 400

    file = request.files["audio_file"]
    if file.filename == "":
        return jsonify({
            "success": False,
            "error": "Tên tệp không hợp lệ.",
            "error_en": "Empty filename."
        }), 400

    if not is_allowed_extension(file.filename):
        return jsonify({
            "success": False,
            "error": "Định dạng không được hỗ trợ. Hãy dùng MP3, WAV, FLAC, M4A, OGG.",
            "error_en": "Unsupported format. Use MP3, WAV, FLAC, M4A, OGG."
        }), 400

    # Lưu tạm tệp vào UPLOAD_FOLDER
    original_name = secure_filename(file.filename) or f"audio_{int(datetime.now().timestamp())}.mp3"
    file_id = f"{uuid.uuid4().hex[:12]}_{original_name}"
    save_path = UPLOAD_FOLDER / file_id
    file.save(str(save_path))

    # Kiểm tra tính hợp lệ (<= 100MB và <= 8 phút)
    is_valid, err_msg, meta = validate_audio_file(save_path)
    if not is_valid:
        # Xóa file vi phạm
        if save_path.exists():
            try:
                os.remove(save_path)
            except Exception:
                pass
        return jsonify({
            "success": False,
            "error": err_msg,
            "error_en": f"Audio validation failed: {err_msg}",
            "metadata": meta
        }), 400

    append_agent_action_log("Upload Audio Thành Công", {
        "Filename": original_name,
        "Dung lượng": meta.get("file_size_formatted"),
        "Thời lượng": meta.get("duration_formatted")
    })

    return jsonify({
        "success": True,
        "file_id": file_id,
        "original_filename": original_name,
        "metadata": meta
    })

def _run_separation_job(
    job_id: str,
    file_id: str,
    input_path: Path,
    model: str,
    device: str,
    output_format: str,
    segment_size: int,
    overlap: int,
    batch_size: int,
    use_autocast: bool,
    audio_duration_seconds: float = 300.0,
):
    """
    Background thread: runs separation and updates job progress.
    Progress is simulated via time-based interpolation within each phase.
    Checks cancel_requested flag at key points to support user cancellation.
    """
    # 1. Model Loading Duration Estimation:
    # If the model is already in RAM cache, loading takes only ~1-2 seconds.
    # Otherwise, large transformer models (RoFormer ~640MB-1.5GB) take 50-80s to deserialize & move to GPU VRAM.
    cache_info = get_cache_status()
    is_model_cached = (
        cache_info.get("loaded", False)
        and cache_info.get("model") == model
        and cache_info.get("device") == device
    )

    if is_model_cached:
        load_est = 2.0
    elif "roformer" in model.lower():
        load_est = 65.0
    elif "demucs" in model.lower():
        load_est = 30.0
    elif "mdx" in model.lower() or model.endswith(".onnx"):
        load_est = 10.0
    else:
        load_est = 25.0

    # 2. Separation Phase Duration Estimation based on audio length & params
    seg_factor = segment_size / 256.0                  # larger segment = slower
    overlap_factor = overlap / 4.0                     # higher overlap = slower
    gpu_est = audio_duration_seconds * 4.0 * seg_factor * overlap_factor
    cpu_est = audio_duration_seconds * 15.0 * seg_factor * overlap_factor
    sep_estimate = gpu_est if device.lower() == "cuda" else cpu_est
    sep_estimate = max(sep_estimate, 30.0)             # at least 30 seconds

    PHASE_DURATIONS = {
        "loading_model": load_est,
        "separating":    sep_estimate,
        "writing":       8,
    }
    PHASE_RANGES = {
        "loading_model": (3,  20),
        "separating":    (20, 90),
        "writing":       (90, 98),
    }

    # Track all active stop events so we can clean them up in finally
    _active_stops = []

    def _smooth_progress(phase_name: str, stop_event: threading.Event):
        """Increment progress smoothly inside a phase until stop_event is set."""
        import math
        dur = PHASE_DURATIONS.get(phase_name, 30.0)
        p_start, p_end = PHASE_RANGES.get(phase_name, (0, 100))
        p_range = p_end - p_start
        start = time.time()
        while not stop_event.is_set():
            elapsed = time.time() - start
            # Asymptotic progression: never hits a dead brick wall, continually creeps forward
            raw_frac = 1.0 - math.exp(-1.8 * (elapsed / max(dur, 1.0)))
            frac = min(raw_frac, 0.96)
            pct = int(p_start + frac * p_range)

            # Dynamic descriptive status labels to inform user of active processing
            label_vi = None
            label_en = None
            if phase_name == "loading_model":
                if is_model_cached:
                    label_vi = "Sử dụng mô hình AI đã nạp sẵn trong bộ nhớ..."
                    label_en = "Using pre-cached AI model in memory..."
                elif elapsed < 12:
                    label_vi = "Đang khởi tạo cấu hình mô hình AI..."
                    label_en = "Initializing AI model configuration..."
                elif elapsed < 35:
                    label_vi = "Đang nạp trọng số mô hình vào GPU..."
                    label_en = "Loading model weights into GPU..."
                else:
                    label_vi = "Đang sẵn sàng mô hình trong VRAM..."
                    label_en = "Finalizing model in GPU VRAM..."
            elif phase_name == "separating":
                if elapsed < dur * 0.35:
                    label_vi = "Đang phân tích phổ tần số âm thanh..."
                    label_en = "Analyzing audio spectrogram..."
                elif elapsed < dur * 0.75:
                    label_vi = "Mạng nơ-ron AI đang tách giọng hát và nhạc..."
                    label_en = "AI extracting Vocals and Music..."
                else:
                    label_vi = "Đang tái tạo tín hiệu âm thanh chất lượng cao..."
                    label_en = "Reconstructing audio stems..."

            update_job_progress(job_id, pct, label_vi=label_vi, label_en=label_en)
            time.sleep(0.5)

    def _start_progress(phase_name: str) -> tuple:
        """Start a smooth-progress thread and register its stop event."""
        stop = threading.Event()
        _active_stops.append(stop)
        t = threading.Thread(target=_smooth_progress, args=(phase_name, stop), daemon=True)
        t.start()
        return stop, t

    class CancelledError(Exception):
        pass

    def _check_cancel():
        if is_cancel_requested(job_id):
            raise CancelledError("Job cancelled by user")

    try:
        # ── Phase 1: Loading model ──────────────────────────────────────────
        _check_cancel()
        update_job_phase(job_id, "loading_model")
        stop1, t1 = _start_progress("loading_model")

        from separator_core.separator_service import _get_separator
        from separator_core.settings_service import get_settings as _gs
        _gs()   # warm settings cache
        # Pre-load / cache the model (this is the slow part of loading_model phase)
        _get_separator(
            model_checkpoint=model,
            device_mode=device,
            output_format=output_format,
            segment_size=segment_size,
            overlap=overlap,
            batch_size=batch_size,
            use_autocast=use_autocast,
        )
        stop1.set()
        t1.join()

        # ── Phase 2: Separating ─────────────────────────────────────────────
        _check_cancel()
        update_job_phase(job_id, "separating")
        stop2, t2 = _start_progress("separating")

        result = process_stem_separation(
            input_audio_file=input_path,
            model_checkpoint=model,
            device_mode=device,
            output_format=output_format,
            segment_size=segment_size,
            overlap=overlap,
            batch_size=batch_size,
            use_autocast=use_autocast,
        )
        stop2.set()
        t2.join()

        # ── Phase 3: Writing / post-processing ─────────────────────────────
        _check_cancel()
        update_job_phase(job_id, "writing")
        stop3, t3 = _start_progress("writing")

        # Lưu lịch sử
        history_entry = {
            "file_id": file_id,
            "original_filename": file_id.split("_", 1)[-1],
            "model_used": model,
            "device_used": result.get("device_used", device),
            "processing_time": f"{result.get('processing_time_seconds', 0)}s",
            "stems": result.get("stems", []),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        added_entry = add_history_entry(history_entry)
        result["history_entry"] = added_entry

        append_agent_action_log("Hoàn Tất Phân Tách Âm Thanh", {
            "File": history_entry["original_filename"],
            "Model": model,
            "Thiết bị": result.get("device_used", device),
            "Thời gian xử lý": f"{result.get('processing_time_seconds', 0)}s",
            "Số lượng stems": len(result.get("stems", []))
        })

        stop3.set()
        t3.join()

        # ── Done ────────────────────────────────────────────────────────────
        complete_job(job_id, result)
        logger.info(f"Job {job_id} completed successfully.")

    except BaseException as e:
        # BaseException catches SystemExit (injected via ctypes for force-cancel)
        # as well as regular Exception subclasses
        if is_cancel_requested(job_id) or isinstance(e, SystemExit):
            logger.info(f"Job {job_id} cancelled by user (caught {type(e).__name__}).")
            cancel_job(job_id)
        else:
            logger.exception(f"Job {job_id} failed")
            fail_job(job_id, str(e))
    finally:
        # Always stop all progress sub-threads (handles cancel, error, and normal exit)
        for stop_evt in _active_stops:
            stop_evt.set()


@app.route("/api/separate", methods=["POST"])
def separate_audio():
    data = request.get_json() or {}
    file_id = data.get("file_id")

    if not file_id:
        return jsonify({
            "success": False,
            "error": "Chưa chọn tệp âm thanh hợp lệ.",
            "error_en": "No valid audio file selected."
        }), 400

    input_path = UPLOAD_FOLDER / file_id
    if not input_path.exists():
        return jsonify({
            "success": False,
            "error": "Tệp âm thanh nguồn đã hết hạn hoặc không tồn tại.",
            "error_en": "Audio source file not found or expired."
        }), 404

    # Đọc cấu hình mong muốn
    current_settings = get_settings()
    model = data.get("model") or current_settings.get("model", "mel_band_roformer_kim_ft3_unwa.ckpt")
    device = data.get("device") or current_settings.get("device", DEFAULT_DEVICE)
    output_format = data.get("output_format") or current_settings.get("output_format", "WAV")
    segment_size = data.get("segment_size") or current_settings.get("segment_size", 256)
    overlap = data.get("overlap") or current_settings.get("overlap", 4)
    batch_size = data.get("batch_size") or current_settings.get("batch_size", 1)

    # Get audio duration for accurate progress estimation
    audio_duration = data.get("audio_duration_seconds") or 300.0

    # Create async job and launch background thread
    job_id = create_job()
    thread = threading.Thread(
        target=_run_separation_job,
        args=(
            job_id, file_id, input_path,
            model, device, output_format,
            segment_size, overlap, batch_size,
            current_settings.get("use_autocast", True),
            float(audio_duration),
        ),
        daemon=True,
    )
    thread.start()
    # Store native thread ID immediately so force-cancel can find it
    set_job_thread_id(job_id, thread.ident)
    logger.info(f"Launched separation job {job_id} for file {file_id} (est. duration: {audio_duration}s, thread: {thread.ident})")

    return jsonify({"success": True, "job_id": job_id})


@app.route("/api/job/<job_id>/status", methods=["GET"])
def job_status(job_id):
    """Poll endpoint for separation job progress."""
    job = get_job(job_id)
    if job is None:
        return jsonify({"success": False, "error": "Job not found."}), 404

    # Don't expose the full result in every poll — only when done
    resp = {
        "success": True,
        "job_id": job_id,
        "status": job["status"],
        "phase_label_vi": job["phase_label_vi"],
        "phase_label_en": job["phase_label_en"],
        "progress_pct": job["progress_pct"],
        "elapsed_seconds": job["elapsed_seconds"],
    }
    if job["status"] == "done":
        resp["result"] = job["result"]
    elif job["status"] in ("error", "cancelled"):
        resp["error"] = job.get("error", "Job was cancelled.")

    return jsonify(resp)


@app.route("/api/job/<job_id>/cancel", methods=["POST"])
def cancel_job_endpoint(job_id):
    """Request cancellation of a running job."""
    found = request_cancel(job_id)
    if found:
        logger.info(f"Cancel requested for job {job_id}")
        return jsonify({"success": True, "message": "Hủy tác vụ đã được gửi."})
    return jsonify({"success": False, "error": "Không tìm thấy tác vụ hoặc đã hoàn tất."}), 404

@app.route("/api/history", methods=["GET", "DELETE"])
def manage_history():
    if request.method == "GET":
        items = get_history()
        return jsonify({"success": True, "history": items, "count": len(items)})
    
    # DELETE: Xóa toàn bộ
    clear_history()
    try:
        from separator_core.lyrics_db import clear_lyrics_history
        clear_lyrics_history()
    except Exception:
        pass
    append_agent_action_log("Xóa Toàn Bộ Lịch Sử", {"Status": "Cleared"})
    return jsonify({"success": True, "message": "Đã xóa toàn bộ lịch sử."})

@app.route("/api/history/<entry_id>", methods=["DELETE"])
def remove_history_item(entry_id):
    items = get_history()
    target = next((item for item in items if item.get("id") == entry_id), None)
    if target and target.get("db_id"):
        try:
            from separator_core.lyrics_db import delete_lyrics_record
            delete_lyrics_record(target["db_id"])
        except Exception:
            pass

    success = delete_history_entry(entry_id)
    if success:
        append_agent_action_log("Xóa Mục Lịch Sử", {"ID": entry_id})
        return jsonify({"success": True, "message": f"Đã xóa bản ghi {entry_id}."})
    return jsonify({"success": False, "error": "Không tìm thấy bản ghi."}), 404

@app.route("/api/audio/<folder>/<path:filename>")
def serve_audio(folder, filename):
    safe_folder = UPLOAD_FOLDER if folder == "uploads" else OUTPUT_FOLDER
    target_path = safe_folder / filename
    if not target_path.exists():
        abort(404)
    return send_from_directory(safe_folder, filename)

@app.route("/api/model_status", methods=["GET"])
def model_status():
    """Trả về trạng thái model cache (đã warm-up chưa)."""
    status = get_cache_status()
    return jsonify({"success": True, "cache": status})


# ── Lyrics / Karaoke Endpoints ────────────────────────────────────────────────

@app.route("/api/lyrics/extract", methods=["POST"])
def lyrics_extract():
    """
    Trích xuất lyrics từ file vocals bằng Whisper STT.
    Body: { "vocals_filename": "xxx_Vocals.wav", "whisper_model": "base", "language": "vi" }
    """
    data = request.get_json() or {}
    vocals_filename = data.get("vocals_filename")
    whisper_model   = data.get("whisper_model", "base")
    language        = data.get("language") or None  # None = auto-detect

    if not vocals_filename:
        return jsonify({"success": False, "error": "Thiếu vocals_filename."}), 400

    vocals_path = OUTPUT_FOLDER / vocals_filename
    if not vocals_path.exists():
        return jsonify({"success": False, "error": f"Không tìm thấy file: {vocals_filename}"}), 404

    try:
        from separator_core.lyrics_service import extract_lyrics_from_vocals
        from separator_core.lyrics_db import save_lyrics_record
        result = extract_lyrics_from_vocals(
            vocals_path=vocals_path,
            whisper_model=whisper_model,
            language=language,
        )

        # ── 1. Ghi nhớ vào SQLite DB (lưu toàn bộ segments, metadata) ─────
        db_id = save_lyrics_record(
            vocals_filename=vocals_filename,
            whisper_model=whisper_model,
            detected_language=result.get("detected_language", "unknown"),
            total_lines=result.get("total_lines", 0),
            srt_filename=result.get("srt_filename", ""),
            lrc_filename=result.get("lrc_filename", ""),
            segments=result.get("segments", []),
            record_type="lyrics"
        )
        result["db_id"] = db_id

        # ── 2. Ghi lịch sử vào history.json để hiển thị đồng bộ ───────────
        lyrics_history_entry = {
            "type":              "lyrics",
            "vocals_filename":   vocals_filename,
            "whisper_model":     whisper_model,
            "detected_language": result.get("detected_language", "unknown"),
            "total_lines":       result.get("total_lines", 0),
            "srt_filename":      result.get("srt_filename", ""),
            "lrc_filename":      result.get("lrc_filename", ""),
            "db_id":             db_id,
            "timestamp":         datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        add_history_entry(lyrics_history_entry)
        # ──────────────────────────────────────────────────────────────────

        append_agent_action_log("Trích Xuất Lyrics", {
            "File": vocals_filename,
            "Model Whisper": whisper_model,
            "Ngôn ngữ phát hiện": result.get("detected_language", "unknown"),
            "Số dòng": result.get("total_lines", 0),
            "DB ID": db_id,
        })
        return jsonify(result)
    except RuntimeError as e:
        return jsonify({"success": False, "error": str(e)}), 500
    except Exception as e:
        logger.exception(f"Lyrics extraction failed for {vocals_filename}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/lyrics/save", methods=["POST"])
def lyrics_save():
    """
    Lưu lại segments đã chỉnh sửa từ Karaoke Editor.
    Body: { "vocals_filename": "xxx_Vocals.wav", "segments": [...] }
    """
    data = request.get_json() or {}
    vocals_filename = data.get("vocals_filename")
    segments        = data.get("segments", [])

    if not vocals_filename or not segments:
        return jsonify({"success": False, "error": "Thiếu vocals_filename hoặc segments."}), 400

    try:
        from separator_core.lyrics_service import save_edited_lyrics
        from separator_core.lyrics_db import save_lyrics_record
        filenames = save_edited_lyrics(
            segments=segments,
            base_filename=vocals_filename,
        )

        # ── 1. Ghi nhớ phiên bản đã sửa vào SQLite DB ────────────────────
        db_id = save_lyrics_record(
            vocals_filename=vocals_filename,
            whisper_model="",
            detected_language="",
            total_lines=len(segments),
            srt_filename=filenames.get("srt_filename", ""),
            lrc_filename=filenames.get("lrc_filename", ""),
            segments=segments,
            record_type="lyrics_edit"
        )
        filenames["db_id"] = db_id

        # ── 2. Ghi lịch sử chỉnh sửa vào history.json ──────────────────────
        edit_history_entry = {
            "type":            "lyrics_edit",
            "vocals_filename": vocals_filename,
            "total_lines":     len(segments),
            "srt_filename":    filenames.get("srt_filename", ""),
            "lrc_filename":    filenames.get("lrc_filename", ""),
            "db_id":           db_id,
            "timestamp":       datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        add_history_entry(edit_history_entry)
        # ──────────────────────────────────────────────────────────────────

        return jsonify({"success": True, **filenames})
    except Exception as e:
        logger.exception(f"Lyrics save failed for {vocals_filename}")
        return jsonify({"success": False, "error": str(e)}), 500


# ── SQLite Database REST APIs cho Lyrics ──────────────────────────────────────

@app.route("/api/lyrics/db/history", methods=["GET"])
def lyrics_db_history():
    """Lấy danh sách các bản ghi trích xuất lyrics từ SQLite DB"""
    try:
        from separator_core.lyrics_db import get_lyrics_history
        limit  = request.args.get("limit", 50, type=int)
        offset = request.args.get("offset", 0, type=int)
        records = get_lyrics_history(limit=limit, offset=offset)
        return jsonify({"success": True, "records": records, "total": len(records)})
    except Exception as e:
        logger.exception("Error getting lyrics DB history")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/lyrics/db/history/<int:record_id>", methods=["GET"])
def lyrics_db_detail(record_id: int):
    """Lấy chi tiết 1 bản ghi lyrics trong SQLite DB (gồm toàn bộ segments JSON)"""
    try:
        from separator_core.lyrics_db import get_lyrics_by_id
        record = get_lyrics_by_id(record_id)
        if not record:
            return jsonify({"success": False, "error": f"Không tìm thấy bản ghi lyrics #{record_id}"}), 404
        return jsonify({"success": True, "record": record})
    except Exception as e:
        logger.exception(f"Error getting lyrics detail #{record_id}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/lyrics/db/history/<int:record_id>", methods=["DELETE"])
def lyrics_db_delete(record_id: int):
    """Xóa một bản ghi lyrics khỏi SQLite DB"""
    try:
        from separator_core.lyrics_db import delete_lyrics_record
        ok = delete_lyrics_record(record_id)
        if ok:
            return jsonify({"success": True, "message": f"Đã xóa bản ghi lyrics #{record_id} khỏi DB"})
        return jsonify({"success": False, "error": f"Không tìm thấy bản ghi #{record_id}"}), 404
    except Exception as e:
        logger.exception(f"Error deleting lyrics record #{record_id}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/lyrics/db/history/clear", methods=["POST"])
def lyrics_db_clear():
    """Xóa toàn bộ bản ghi lyrics trong SQLite DB"""
    try:
        from separator_core.lyrics_db import clear_lyrics_history
        clear_lyrics_history()
        return jsonify({"success": True, "message": "Đã xóa toàn bộ lịch sử lyrics trong DB"})
    except Exception as e:
        logger.exception("Error clearing lyrics DB history")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/lyrics/<path:filename>/<string:fmt>", methods=["GET"])
def lyrics_download(filename: str, fmt: str):
    """
    Phục vụ file lyrics đã xuất.
    fmt: 'srt' hoặc 'lrc'
    """
    if fmt not in ("srt", "lrc"):
        return jsonify({"success": False, "error": "Định dạng không hợp lệ. Dùng 'srt' hoặc 'lrc'."}), 400

    # Build expected lyrics filename from vocals filename
    import re as _re
    base_name = _re.sub(r"\.[^.]+$", "", filename)
    lyrics_filename = f"{base_name}_lyrics.{fmt}"
    target_path = OUTPUT_FOLDER / lyrics_filename

    if not target_path.exists():
        return jsonify({"success": False, "error": f"File lyrics chưa được tạo: {lyrics_filename}"}), 404

    mime = "text/srt" if fmt == "srt" else "text/plain"
    return send_from_directory(OUTPUT_FOLDER, lyrics_filename,
                               mimetype=mime, as_attachment=True,
                               download_name=lyrics_filename)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    logger.info(f"Starting AI Music Separation Backend API on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=False)
