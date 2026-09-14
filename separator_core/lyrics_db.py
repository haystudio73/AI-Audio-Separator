"""
lyrics_db.py — SQLite Database Manager for Lyrics Extraction & Karaoke History
Quản lý lưu trữ lịch sử trích xuất lời bài hát (Whisper STT), các segments, SRT, LRC vào DB SQLite.
"""

import json
import sqlite3
import threading
from datetime import datetime
from typing import List, Dict, Any, Optional
from config import LYRICS_DB_FILE

_lock = threading.Lock()

def _get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(LYRICS_DB_FILE), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_lyrics_db() -> None:
    """Khởi tạo bảng và index trong database SQLite nếu chưa tồn tại"""
    with _lock:
        conn = _get_connection()
        try:
            with conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS lyrics_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        vocals_filename TEXT NOT NULL,
                        original_filename TEXT,
                        whisper_model TEXT,
                        detected_language TEXT,
                        total_lines INTEGER DEFAULT 0,
                        srt_filename TEXT,
                        lrc_filename TEXT,
                        segments_json TEXT,
                        type TEXT DEFAULT 'lyrics',
                        created_at TEXT,
                        updated_at TEXT
                    );
                """)
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_lyrics_vocals ON lyrics_history(vocals_filename);
                """)
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_lyrics_created ON lyrics_history(created_at DESC);
                """)
        finally:
            conn.close()

# Auto-initialize DB on import
init_lyrics_db()

def save_lyrics_record(
    vocals_filename: str,
    whisper_model: str = "base",
    detected_language: str = "unknown",
    total_lines: int = 0,
    srt_filename: str = "",
    lrc_filename: str = "",
    segments: Optional[List[Dict[str, Any]]] = None,
    record_type: str = "lyrics",
    original_filename: Optional[str] = None
) -> int:
    """
    Lưu một bản ghi trích xuất hoặc chỉnh sửa lyrics vào DB SQLite.
    Trả về ID của bản ghi vừa tạo.
    """
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    segments_json_str = json.dumps(segments or [], ensure_ascii=False)

    with _lock:
        conn = _get_connection()
        try:
            with conn:
                cursor = conn.execute("""
                    INSERT INTO lyrics_history (
                        vocals_filename,
                        original_filename,
                        whisper_model,
                        detected_language,
                        total_lines,
                        srt_filename,
                        lrc_filename,
                        segments_json,
                        type,
                        created_at,
                        updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """, (
                    vocals_filename,
                    original_filename or vocals_filename,
                    whisper_model,
                    detected_language,
                    total_lines,
                    srt_filename,
                    lrc_filename,
                    segments_json_str,
                    record_type,
                    now_str,
                    now_str
                ))
                return cursor.lastrowid
        finally:
            conn.close()

def get_lyrics_history(limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
    """
    Lấy danh sách lịch sử lyrics từ DB (sắp xếp mới nhất trước).
    Không trả về trường segments_json lớn để tối ưu hiệu năng danh sách.
    """
    with _lock:
        conn = _get_connection()
        try:
            cursor = conn.execute("""
                SELECT id, vocals_filename, original_filename, whisper_model,
                       detected_language, total_lines, srt_filename, lrc_filename,
                       type, created_at, updated_at
                FROM lyrics_history
                ORDER BY id DESC
                LIMIT ? OFFSET ?;
            """, (limit, offset))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

def get_lyrics_by_id(record_id: int) -> Optional[Dict[str, Any]]:
    """
    Lấy chi tiết 1 bản ghi lyrics theo ID, bao gồm toàn bộ segments đã parse JSON.
    """
    with _lock:
        conn = _get_connection()
        try:
            cursor = conn.execute("""
                SELECT * FROM lyrics_history WHERE id = ?;
            """, (record_id,))
            row = cursor.fetchone()
            if not row:
                return None
            data = dict(row)
            try:
                data["segments"] = json.loads(data.get("segments_json") or "[]")
            except Exception:
                data["segments"] = []
            return data
        finally:
            conn.close()

def get_latest_lyrics_for_file(vocals_filename: str) -> Optional[Dict[str, Any]]:
    """
    Lấy bản ghi lyrics mới nhất của một file vocals cụ thể.
    """
    with _lock:
        conn = _get_connection()
        try:
            cursor = conn.execute("""
                SELECT * FROM lyrics_history 
                WHERE vocals_filename = ?
                ORDER BY id DESC
                LIMIT 1;
            """, (vocals_filename,))
            row = cursor.fetchone()
            if not row:
                return None
            data = dict(row)
            try:
                data["segments"] = json.loads(data.get("segments_json") or "[]")
            except Exception:
                data["segments"] = []
            return data
        finally:
            conn.close()

def delete_lyrics_record(record_id: int) -> bool:
    """Xóa một bản ghi lyrics theo ID khỏi DB SQLite"""
    with _lock:
        conn = _get_connection()
        try:
            with conn:
                cursor = conn.execute("""
                    DELETE FROM lyrics_history WHERE id = ?;
                """, (record_id,))
                return cursor.rowcount > 0
        finally:
            conn.close()

def clear_lyrics_history() -> bool:
    """Xóa toàn bộ lịch sử lyrics trong DB SQLite"""
    with _lock:
        conn = _get_connection()
        try:
            with conn:
                conn.execute("DELETE FROM lyrics_history;")
                return True
        finally:
            conn.close()
