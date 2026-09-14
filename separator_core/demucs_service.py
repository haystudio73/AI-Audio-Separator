"""
Demucs Native Service — Method 1 from:
https://dev.to/stevecase430/how-to-remove-vocals-from-any-song-using-python-3-methods-28pa

Uses the `demucs` library directly (python -m demucs) via subprocess,
which is the native Demucs approach — separate from audio-separator pipeline.

Called automatically by separator_service.py when model is a .yaml (Demucs) config.
"""
import os
import sys
import time
import shutil
import logging
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional

from config import OUTPUT_FOLDER, IS_CUDA_AVAILABLE
from separator_core.audio_utils import get_audio_info

logger = logging.getLogger(__name__)

# Default Demucs model name (matches htdemucs.yaml curated model)
DEFAULT_DEMUCS_MODEL = "htdemucs"

# Stem name mappings for Demucs output folders
STEM_DISPLAY_NAMES = {
    "vocals": "Vocals",
    "no_vocals": "Instrumental",
    "drums": "Drums",
    "bass": "Bass",
    "other": "Other",
    "guitar": "Guitar",
    "piano": "Piano",
}


def _yaml_to_model_name(model_filename: str) -> str:
    """
    Map a .yaml config filename to the Demucs model name string.
    e.g. 'htdemucs.yaml' -> 'htdemucs'
         'htdemucs_ft.yaml' -> 'htdemucs_ft'
    """
    return Path(model_filename).stem


def _get_demucs_output_dir(base_output: Path, model_name: str, input_stem: str) -> Optional[Path]:
    """
    Demucs writes: <output_dir>/<model_name>/<track_name_without_ext>/
    Try to locate the folder that Demucs created for this track.
    """
    model_dir = base_output / model_name
    if model_dir.exists():
        # Find subdirectory matching input stem
        candidates = [d for d in model_dir.iterdir() if d.is_dir()]
        if candidates:
            # Return the most recently created subdir if multiple
            return max(candidates, key=lambda p: p.stat().st_mtime)
    return None


def _collect_output_files(
    demucs_out_dir: Path,
    output_format: str,
    input_name: str,
    model_name: str,
) -> list[Dict[str, Any]]:
    """
    Scan the Demucs output directory, copy stems to OUTPUT_FOLDER,
    and return a list of stem info dicts compatible with separator_service schema.
    """
    stems = []
    ext = output_format.lower()
    if ext not in ("wav", "mp3", "flac"):
        ext = "wav"

    # Demucs outputs WAV by default; if user wants mp3/flac we'd need extra conversion.
    # Collect all audio files in the demucs output folder.
    audio_exts = {".wav", ".mp3", ".flac", ".ogg"}
    stem_files = [f for f in demucs_out_dir.iterdir()
                  if f.is_file() and f.suffix.lower() in audio_exts]

    for stem_file in sorted(stem_files):
        stem_key = stem_file.stem.lower()  # e.g. 'vocals', 'drums', 'bass', 'other'
        display_name = STEM_DISPLAY_NAMES.get(stem_key, stem_key.capitalize())

        # Build output filename: <input_name>_(Demucs_<StemName>).<ext>
        dest_name = f"{Path(input_name).stem}_(Demucs_{display_name}){stem_file.suffix}"
        dest_path = OUTPUT_FOLDER / dest_name

        try:
            shutil.copy2(stem_file, dest_path)
            logger.info(f"Copied Demucs stem: {stem_file.name} -> {dest_name}")
        except Exception as e:
            logger.warning(f"Failed to copy stem {stem_file}: {e}")
            continue

        audio_info = get_audio_info(dest_path)
        stems.append({
            "stem_name": display_name,
            "filename": dest_name,
            "download_url": f"/api/audio/outputs/{dest_name}",
            "file_size": audio_info.get("file_size", 0),
            "file_size_formatted": audio_info.get("file_size_formatted", "0 B"),
            "duration_seconds": audio_info.get("duration_seconds", 0.0),
            "duration_formatted": audio_info.get("duration_formatted", "00:00"),
            "format": audio_info.get("format", output_format.upper()),
        })

    return stems


def process_demucs_separation(
    input_audio_file: str | Path,
    model_filename: str = "htdemucs.yaml",
    device_mode: str = "cuda",
    output_format: str = "WAV",
    two_stems: Optional[str] = None,  # e.g. "vocals" to get vocals + no_vocals only
) -> Dict[str, Any]:
    """
    Run Demucs natively using `python -m demucs` subprocess (Method 1).

    This is equivalent to running in terminal:
        python -m demucs --two-stems=vocals -d cuda -o <output_dir> <input_file>

    Args:
        input_audio_file: Path to input audio file.
        model_filename:   Demucs yaml filename (e.g. 'htdemucs.yaml').
        device_mode:      'cuda' or 'cpu'.
        output_format:    Desired output format (wav/mp3/flac). Demucs natively outputs WAV.
        two_stems:        If set (e.g. 'vocals'), use --two-stems flag for faster 2-stem separation.

    Returns:
        Dict with success, stems list, processing time, etc.
    """
    start_time = time.time()
    input_audio_file = Path(input_audio_file)
    if not input_audio_file.exists():
        raise FileNotFoundError(f"Input audio file not found: {input_audio_file}")

    model_name = _yaml_to_model_name(model_filename)
    device = "cuda" if (device_mode.lower() == "cuda" and IS_CUDA_AVAILABLE) else "cpu"

    # Demucs writes output to: <out_dir>/<model_name>/<track_stem>/
    # We use OUTPUT_FOLDER as the Demucs output root.
    demucs_out_root = OUTPUT_FOLDER / "_demucs_tmp"
    os.makedirs(demucs_out_root, exist_ok=True)
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    # Build Demucs CLI command (Method 1 from article)
    cmd = [
        sys.executable, "-m", "demucs",
        "--name", model_name,
        "-d", device,
        "-o", str(demucs_out_root),
    ]
    if two_stems:
        cmd += ["--two-stems", two_stems]

    cmd.append(str(input_audio_file))

    logger.info(f"[Demucs] Running: {' '.join(cmd)}")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if result.returncode != 0:
            err = result.stderr or result.stdout or "Unknown error"
            logger.error(f"[Demucs] Subprocess failed (code {result.returncode}): {err}")
            raise RuntimeError(f"Demucs separation failed: {err[:500]}")

        logger.info(f"[Demucs] stdout: {result.stdout[-500:] if result.stdout else ''}")

    except FileNotFoundError:
        raise RuntimeError(
            "Demucs is not installed. Please run: pip install demucs"
        )

    elapsed_time = round(time.time() - start_time, 2)

    # Locate the output directory Demucs created
    input_stem_name = input_audio_file.stem
    demucs_out_dir = _get_demucs_output_dir(demucs_out_root, model_name, input_stem_name)

    if demucs_out_dir is None or not demucs_out_dir.exists():
        raise RuntimeError(
            f"Demucs output directory not found under {demucs_out_root / model_name}. "
            f"Demucs stderr: {result.stderr[:300] if result.stderr else 'N/A'}"
        )

    logger.info(f"[Demucs] Output directory: {demucs_out_dir}")

    # Collect and copy stems to OUTPUT_FOLDER
    stems = _collect_output_files(
        demucs_out_dir=demucs_out_dir,
        output_format=output_format,
        input_name=input_audio_file.name,
        model_name=model_name,
    )

    # Clean up temporary Demucs output folder
    try:
        shutil.rmtree(demucs_out_root, ignore_errors=True)
        logger.info(f"[Demucs] Cleaned up tmp dir: {demucs_out_root}")
    except Exception as cleanup_err:
        logger.warning(f"[Demucs] Cleanup failed: {cleanup_err}")

    logger.info(f"[Demucs] Separation completed in {elapsed_time}s. Stems: {[s['stem_name'] for s in stems]}")

    return {
        "success": True,
        "input_filename": input_audio_file.name,
        "model_used": model_filename,
        "engine": "demucs",
        "device_used": device,
        "processing_time_seconds": elapsed_time,
        "stems": stems,
    }
