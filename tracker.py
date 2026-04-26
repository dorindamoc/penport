from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from platformdirs import user_data_dir

_APP_NAME = "Penport"


def _db_path() -> Path:
    data_dir = Path(user_data_dir(_APP_NAME, appauthor=False))
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir / "tracker.db"


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(str(_db_path()))
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    print(f"Initializing database at {_db_path()}")
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS jobs (
                id             INTEGER PRIMARY KEY,
                filename       TEXT NOT NULL,
                inbox_path     TEXT NOT NULL UNIQUE,
                processed_at   TEXT NOT NULL,
                status         TEXT NOT NULL,
                output_path    TEXT,
                raw_text       TEXT,
                corrected_text TEXT,
                error_message  TEXT
            )
            """
        )


def is_processed(inbox_path: str) -> bool:
    with _connect() as conn:
        row = conn.execute("SELECT id FROM jobs WHERE inbox_path = ?", (inbox_path,)).fetchone()
        return row is not None


def record_success(
    filename: str,
    inbox_path: str,
    output_path: str,
    raw_text: str,
    corrected_text: str,
) -> None:
    now = datetime.now(timezone.utc).isoformat()
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO jobs
                (filename, inbox_path, processed_at, status, output_path, raw_text, corrected_text)
            VALUES (?, ?, ?, 'success', ?, ?, ?)
            """,
            (filename, inbox_path, now, output_path, raw_text, corrected_text),
        )


def record_error(filename: str, inbox_path: str, error_message: str) -> None:
    now = datetime.now(timezone.utc).isoformat()
    with _connect() as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO jobs
                (filename, inbox_path, processed_at, status, error_message)
            VALUES (?, ?, ?, 'error', ?)
            """,
            (filename, inbox_path, now, error_message),
        )


def get_recent_jobs(limit: int = 50) -> list[dict]:
    with _connect() as conn:
        rows = conn.execute(
            "SELECT * FROM jobs ORDER BY processed_at DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(r) for r in rows]


def get_last_output_path() -> str | None:
    with _connect() as conn:
        row = conn.execute(
            "SELECT output_path FROM jobs WHERE status = 'success' ORDER BY processed_at DESC LIMIT 1"
        ).fetchone()
        return row["output_path"] if row else None
