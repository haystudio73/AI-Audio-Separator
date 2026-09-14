import json
import os
import threading
from typing import List, Dict, Any, Optional
from datetime import datetime
from config import HISTORY_FILE, MAX_HISTORY_ITEMS

_lock = threading.Lock()

def _load_raw_history() -> List[Dict[str, Any]]:
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            return []
    except Exception:
        return []

def _save_raw_history(items: List[Dict[str, Any]]) -> None:
    # Đảm bảo danh sách không vượt quá MAX_HISTORY_ITEMS (67)
    if len(items) > MAX_HISTORY_ITEMS:
        items = items[:MAX_HISTORY_ITEMS]
    
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

def get_history() -> List[Dict[str, Any]]:
    """Lấy danh sách lịch sử xử lý (mới nhất lên đầu)"""
    with _lock:
        return _load_raw_history()

def add_history_entry(entry: Dict[str, Any]) -> Dict[str, Any]:
    """
    Thêm một bản ghi lịch sử mới.
    Tự động gắn timestamp và id nếu chưa có.
    Giữ tối đa đúng 67 mục (FIFO - mục cũ nhất bị xóa khi vượt quá).
    """
    with _lock:
        items = _load_raw_history()
        
        if "id" not in entry:
            entry["id"] = f"hist_{int(datetime.now().timestamp() * 1000)}"
        if "timestamp" not in entry:
            entry["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Chèn lên đầu danh sách (mới nhất)
        items.insert(0, entry)
        
        # Cắt bớt nếu vượt quá giới hạn 67
        if len(items) > MAX_HISTORY_ITEMS:
            items = items[:MAX_HISTORY_ITEMS]
            
        _save_raw_history(items)
        return entry

def delete_history_entry(entry_id: str) -> bool:
    """Xóa một bản ghi lịch sử theo ID"""
    with _lock:
        items = _load_raw_history()
        new_items = [item for item in items if item.get("id") != entry_id]
        if len(new_items) != len(items):
            _save_raw_history(new_items)
            return True
        return False

def clear_history() -> None:
    """Xóa toàn bộ lịch sử"""
    with _lock:
        _save_raw_history([])
