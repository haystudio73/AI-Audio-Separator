import os
from pathlib import Path
import torch

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
UPLOAD_FOLDER = DATA_DIR / "uploads"
OUTPUT_FOLDER = DATA_DIR / "outputs"
MODEL_FOLDER = DATA_DIR / "models"
NUMBA_CACHE_DIR = DATA_DIR / "numba_cache"
AGENT_DIR = BASE_DIR / ".agent"

# Fix Numba cache permission issue when Python is in write-protected directory (e.g. C:\Program Files)
os.makedirs(NUMBA_CACHE_DIR, exist_ok=True)
os.environ["NUMBA_CACHE_DIR"] = str(NUMBA_CACHE_DIR)

SETTINGS_FILE = BASE_DIR / "settings.json"
HISTORY_FILE = BASE_DIR / "history.json"
LYRICS_DB_FILE = DATA_DIR / "lyrics.db"

# Audio upload limits
MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100 MB
MAX_AUDIO_DURATION_SECONDS = 480         # 8 minutes (480 seconds)
ALLOWED_EXTENSIONS = {"mp3", "wav", "flac", "m4a", "ogg", "aac", "wma"}

# History limits
MAX_HISTORY_ITEMS = 67

# CUDA Detection
IS_CUDA_AVAILABLE = torch.cuda.is_available()
DEFAULT_DEVICE = "cuda" if IS_CUDA_AVAILABLE else "cpu"

# Default Model & Performance Options
DEFAULT_SETTINGS = {
    "device": DEFAULT_DEVICE,
    "model": "htdemucs.yaml",
    "output_format": "MP3",
    "theme": "dark",
    "language": "vi",
    "segment_size": 256,
    "overlap": 4,
    "batch_size": 1,
    "use_autocast": True
}

# Ensure required directories exist
for folder in [DATA_DIR, UPLOAD_FOLDER, OUTPUT_FOLDER, MODEL_FOLDER, AGENT_DIR]:
    os.makedirs(folder, exist_ok=True)
