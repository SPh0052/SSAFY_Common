import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional

DB_PATH = Path(__file__).parent / "archive.db"

def get_conn():
    return sqlite3.connect(DB_PATH)

def init_db():
    with get_conn() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_name TEXT NOT NULL,
            item_type TEXT NOT NULL,          -- "photo" or "document"
            taken_date TEXT,
            camera_make TEXT,
            camera_model TEXT,
            gps_lat REAL,
            gps_lon REAL,
            objects TEXT,                     -- comma-separated
            keywords TEXT,                    -- comma-separated
            created_at TEXT DEFAULT (datetime('now'))
        )
        """)
        conn.commit()

def insert_photo(
    file_name: str,
    taken_date: Optional[str],
    camera_make: Optional[str],
    camera_model: Optional[str],
    gps_lat: Optional[float],
    gps_lon: Optional[float],
    objects: List[str],
    keywords: List[str],
):
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO items
            (file_name, item_type, taken_date, camera_make, camera_model, gps_lat, gps_lon, objects, keywords)
            VALUES (?, 'photo', ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                file_name,
                taken_date,
                camera_make,
                camera_model,
                gps_lat,
                gps_lon,
                ",".join(objects),
                ",".join(keywords),
            ),
        )
        conn.commit()

def search_items(query: str) -> List[Dict[str, Any]]:
    q = query.strip()
    if not q:
        return []

    like = f"%{q}%"
    with get_conn() as conn:
        cur = conn.execute(
            """
            SELECT id, file_name, item_type, taken_date, camera_make, camera_model, gps_lat, gps_lon, objects, keywords, created_at
            FROM items
            WHERE keywords LIKE ? OR objects LIKE ? OR file_name LIKE ? OR taken_date LIKE ? OR camera_make LIKE ? OR camera_model LIKE ?
            ORDER BY id DESC
            """,
            (like, like, like, like, like, like),
        )
        rows = cur.fetchall()

    cols = ["id","file_name","item_type","taken_date","camera_make","camera_model","gps_lat","gps_lon","objects","keywords","created_at"]
    return [dict(zip(cols, r)) for r in rows]

def list_photos_with_location() -> List[Dict[str, Any]]:
    with get_conn() as conn:
        cur = conn.execute(
            """
            SELECT id, file_name, gps_lat, gps_lon, taken_date, keywords
            FROM items
            WHERE item_type='photo' AND gps_lat IS NOT NULL AND gps_lon IS NOT NULL
            ORDER BY id DESC
            """
        )
        rows = cur.fetchall()

    cols = ["id","file_name","gps_lat","gps_lon","taken_date","keywords"]
    return [dict(zip(cols, r)) for r in rows]
