import json
import os
import threading
from typing import Dict, Any
from config import SETTINGS_FILE, DEFAULT_SETTINGS

_lock = threading.Lock()

def get_settings() -> Dict[str, Any]:
    with _lock:
        if not os.path.exists(SETTINGS_FILE):
            save_settings(DEFAULT_SETTINGS)
            return dict(DEFAULT_SETTINGS)
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
                # Merge with defaults in case of missing keys
                merged = dict(DEFAULT_SETTINGS)
                merged.update(saved)
                return merged
        except Exception:
            return dict(DEFAULT_SETTINGS)

def save_settings(new_settings: Dict[str, Any]) -> Dict[str, Any]:
    with _lock:
        current = {}
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                    current = json.load(f)
            except Exception:
                current = dict(DEFAULT_SETTINGS)
        else:
            current = dict(DEFAULT_SETTINGS)

        current.update(new_settings)
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(current, f, ensure_ascii=False, indent=2)
        return current
