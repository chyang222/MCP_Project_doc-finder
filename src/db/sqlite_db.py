import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
import config


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(config.SQLITE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT UNIQUE NOT NULL,
                file_name TEXT NOT NULL,
                extension TEXT NOT NULL,
                last_modified REAL NOT NULL,
                indexed_at REAL NOT NULL,
                total_pages INTEGER DEFAULT 0
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_id INTEGER NOT NULL,
                page INTEGER NOT NULL,
                page_label TEXT NOT NULL,
                text TEXT NOT NULL,
                chroma_id TEXT NOT NULL,
                FOREIGN KEY (file_id) REFERENCES files(id)
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_chunks_file_id ON chunks(file_id)")
        conn.commit()


def get_file_record(file_path: str) -> dict | None:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM files WHERE file_path = ?", (file_path,)
        ).fetchone()
        return dict(row) if row else None


def upsert_file(file_path: str, file_name: str, extension: str, last_modified: float, total_pages: int) -> int:
    import time
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO files (file_path, file_name, extension, last_modified, indexed_at, total_pages)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(file_path) DO UPDATE SET
                last_modified = excluded.last_modified,
                indexed_at = excluded.indexed_at,
                total_pages = excluded.total_pages
        """, (file_path, file_name, extension, last_modified, time.time(), total_pages))
        conn.commit()
        row = conn.execute("SELECT id FROM files WHERE file_path = ?", (file_path,)).fetchone()
        return row["id"]


def delete_chunks_by_file(file_id: int) -> list[str]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT chroma_id FROM chunks WHERE file_id = ?", (file_id,)
        ).fetchall()
        chroma_ids = [r["chroma_id"] for r in rows]
        conn.execute("DELETE FROM chunks WHERE file_id = ?", (file_id,))
        conn.commit()
        return chroma_ids


def insert_chunks(file_id: int, chunks: list[dict]):
    with get_connection() as conn:
        conn.executemany("""
            INSERT INTO chunks (file_id, page, page_label, text, chroma_id)
            VALUES (:file_id, :page, :page_label, :text, :chroma_id)
        """, [{"file_id": file_id, **c} for c in chunks])
        conn.commit()


def get_chunk_by_chroma_id(chroma_id: str) -> dict | None:
    with get_connection() as conn:
        row = conn.execute("""
            SELECT c.page, c.page_label, c.text, f.file_name, f.file_path
            FROM chunks c
            JOIN files f ON c.file_id = f.id
            WHERE c.chroma_id = ?
        """, (chroma_id,)).fetchone()
        return dict(row) if row else None
