"""
job_manager.py — Thread-safe async job management for audio separation.

Each job goes through these phases:
  queued → loading_model → separating → writing → done / error

Progress % is simulated/estimated from elapsed time and phase weights.
"""
import threading
import time
import uuid
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# ── Phase definitions ────────────────────────────────────────────────────────
# (name, label_vi, label_en, estimated_seconds, progress_start, progress_end)
PHASES = [
    ("queued",        "Đang chuẩn bị...",          "Preparing...",             1,   0,   3),
    ("loading_model", "Đang tải mô hình AI...",     "Loading AI model...",     18,   3,  20),
    ("separating",    "Đang phân tách âm thanh...", "Separating audio...",    110,  20,  90),
    ("writing",       "Đang ghi kết quả...",        "Writing output files...",  8,  90,  98),
    ("done",          "Hoàn tất!",                  "Done!",                    0, 100, 100),
]

PHASE_MAP = {p[0]: p for p in PHASES}

# ── In-memory job store ───────────────────────────────────────────────────────
_jobs: Dict[str, Dict[str, Any]] = {}
_jobs_lock = threading.Lock()


def create_job() -> str:
    """Create a new job entry; returns the job_id."""
    job_id = uuid.uuid4().hex
    with _jobs_lock:
        _jobs[job_id] = {
            "job_id": job_id,
            "status": "queued",          # queued|loading_model|separating|writing|done|error|cancelled
            "phase_label_vi": "Đang chuẩn bị...",
            "phase_label_en": "Preparing...",
            "progress_pct": 0,
            "elapsed_seconds": 0.0,
            "result": None,
            "error": None,
            "cancel_requested": False,
            "thread_id": None,           # native OS thread ID for force-cancel
            "created_at": time.time(),
            "updated_at": time.time(),
        }
    return job_id


def set_job_thread_id(job_id: str, thread_id: int):
    """Store the worker thread's native ID so we can force-cancel it."""
    with _jobs_lock:
        job = _jobs.get(job_id)
        if job:
            job["thread_id"] = thread_id


def update_job_phase(job_id: str, phase: str):
    """Transition a job to a new phase."""
    p = PHASE_MAP.get(phase)
    if not p:
        return
    with _jobs_lock:
        job = _jobs.get(job_id)
        if job:
            job["status"] = phase
            job["phase_label_vi"] = p[1]
            job["phase_label_en"] = p[2]
            job["progress_pct"] = p[4]   # start of phase
            job["updated_at"] = time.time()


def update_job_progress(job_id: str, pct: int, label_vi: Optional[str] = None, label_en: Optional[str] = None):
    """Directly set the progress percentage (0-100) and optional status labels."""
    with _jobs_lock:
        job = _jobs.get(job_id)
        if job:
            job["progress_pct"] = max(0, min(100, pct))
            job["elapsed_seconds"] = round(time.time() - job["created_at"], 1)
            if label_vi:
                job["phase_label_vi"] = label_vi
            if label_en:
                job["phase_label_en"] = label_en
            job["updated_at"] = time.time()


def update_job_status_label(job_id: str, label_vi: str, label_en: str = ""):
    """Update only the human-readable phase label."""
    with _jobs_lock:
        job = _jobs.get(job_id)
        if job:
            job["phase_label_vi"] = label_vi
            if label_en:
                job["phase_label_en"] = label_en
            job["updated_at"] = time.time()


def complete_job(job_id: str, result: Dict[str, Any]):
    """Mark a job as done and store its result."""
    with _jobs_lock:
        job = _jobs.get(job_id)
        if job:
            job["status"] = "done"
            job["phase_label_vi"] = "Hoàn tất!"
            job["phase_label_en"] = "Done!"
            job["progress_pct"] = 100
            job["elapsed_seconds"] = round(time.time() - job["created_at"], 1)
            job["result"] = result
            job["updated_at"] = time.time()


def fail_job(job_id: str, error: str):
    """Mark a job as failed with an error message."""
    with _jobs_lock:
        job = _jobs.get(job_id)
        if job:
            job["status"] = "error"
            job["phase_label_vi"] = "Lỗi xử lý"
            job["phase_label_en"] = "Processing error"
            job["progress_pct"] = 0
            job["elapsed_seconds"] = round(time.time() - job["created_at"], 1)
            job["error"] = error
            job["updated_at"] = time.time()


def request_cancel(job_id: str) -> bool:
    """
    Request cancellation of a running job.
    Step 1: Set cancel_requested flag (for cooperative cancellation at checkpoints).
    Step 2: Force-inject SystemExit into the blocked worker thread via ctypes
            so it interrupts immediately even if stuck inside separator.separate().
    Returns True if the job was found and signal was sent.
    """
    with _jobs_lock:
        job = _jobs.get(job_id)
        if not job or job["status"] in ("done", "error", "cancelled"):
            return False
        job["cancel_requested"] = True
        job["phase_label_vi"] = "Đang dừng..."
        job["phase_label_en"] = "Cancelling..."
        job["updated_at"] = time.time()
        thread_id = job.get("thread_id")

    # Force-inject exception into blocked thread (works even during GPU inference)
    if thread_id:
        _inject_exception_in_thread(thread_id, SystemExit)
        logger.info(f"Injected SystemExit into thread {thread_id} for job {job_id}")

    return True


def _inject_exception_in_thread(thread_id: int, exception_type) -> bool:
    """
    Use CPython's ctypes API to asynchronously raise an exception in another thread.
    This is the only reliable way to interrupt a blocking C-extension (PyTorch/ONNX) call.
    Returns True if the injection succeeded.
    """
    import ctypes
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
        ctypes.c_ulong(thread_id),
        ctypes.py_object(exception_type),
    )
    # res == 0: thread not found, res == 1: success, res > 1: too many threads affected (undo)
    if res > 1:
        # Undo the injection to prevent side effects
        ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_ulong(thread_id), None)
        logger.error(f"PyThreadState_SetAsyncExc affected {res} threads — undone.")
        return False
    return res == 1


def is_cancel_requested(job_id: str) -> bool:
    """Check whether cancellation has been requested for this job."""
    with _jobs_lock:
        job = _jobs.get(job_id)
        return bool(job and job.get("cancel_requested", False))


def cancel_job(job_id: str):
    """Mark a job as cancelled (called from the worker thread when it catches the injected exception)."""
    with _jobs_lock:
        job = _jobs.get(job_id)
        if job:
            job["status"] = "cancelled"
            job["phase_label_vi"] = "Đã dừng"
            job["phase_label_en"] = "Cancelled"
            job["progress_pct"] = 0
            job["elapsed_seconds"] = round(time.time() - job["created_at"], 1)
            job["thread_id"] = None
            job["updated_at"] = time.time()


def get_job(job_id: str) -> Optional[Dict[str, Any]]:
    """Return a snapshot of the job state (thread-safe copy)."""
    with _jobs_lock:
        job = _jobs.get(job_id)
        if job:
            return dict(job)   # shallow copy is fine (result is immutable once set)
        return None


def cleanup_old_jobs(max_age_seconds: int = 3600):
    """Remove jobs older than max_age_seconds (call periodically if needed)."""
    now = time.time()
    with _jobs_lock:
        to_remove = [
            jid for jid, j in _jobs.items()
            if now - j["created_at"] > max_age_seconds
        ]
        for jid in to_remove:
            del _jobs[jid]
    if to_remove:
        logger.info(f"Cleaned up {len(to_remove)} old jobs.")
