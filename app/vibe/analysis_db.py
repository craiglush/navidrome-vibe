"""Read access to the track_analysis SQLite DB (written by the analyzer service).

Schema is defined here too so tests (and an empty first run) can create it.
All queries use parameterized placeholders — no string-built SQL.
"""

import os
import sqlite3

_SCHEMA = """
CREATE TABLE IF NOT EXISTS track_analysis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT UNIQUE NOT NULL,
    title TEXT,
    artist TEXT,
    album TEXT,
    bpm REAL,
    danceability REAL,
    mood_happy REAL,
    mood_sad REAL,
    mood_relaxed REAL,
    mood_aggressive REAL,
    mood_party REAL,
    energy REAL,
    analyzed_at REAL,
    genre TEXT DEFAULT '',
    genre_normalized TEXT DEFAULT '',
    arousal REAL DEFAULT 0.0,
    valence REAL DEFAULT 0.0
);
"""


class AnalysisDB:
    def __init__(self, path: str):
        self.path = path

    def _connect(self):
        os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
        conn = sqlite3.connect(self.path, timeout=30)
        conn.row_factory = sqlite3.Row
        return conn

    def init_schema(self):
        conn = self._connect()
        try:
            conn.executescript(_SCHEMA)
            conn.commit()
        finally:
            conn.close()

    def all_tracks(self):
        conn = self._connect()
        try:
            rows = conn.execute("SELECT * FROM track_analysis").fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    def count(self) -> int:
        conn = self._connect()
        try:
            return conn.execute("SELECT COUNT(*) FROM track_analysis").fetchone()[0]
        finally:
            conn.close()
