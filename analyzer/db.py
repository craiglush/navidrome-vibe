"""Writes the track_analysis SQLite DB that the companion app reads.

The schema here MUST match app/vibe/analysis_db.py exactly (same file, shared volume).
All SQL uses parameterized placeholders for values.
"""

import os
import sqlite3
import time

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

_TEXT_COLS = {"title", "artist", "album", "genre", "genre_normalized"}
_COLUMNS = ["file_path", "title", "artist", "album", "bpm", "danceability",
            "mood_happy", "mood_sad", "mood_relaxed", "mood_aggressive", "mood_party",
            "energy", "genre", "genre_normalized", "arousal", "valence"]

# safe: column names below are this fixed internal constant (never user input);
# all VALUES are bound via ? placeholders, so this is not SQL injection.
_INSERT_SQL = ("INSERT OR REPLACE INTO track_analysis ("
               + ",".join(_COLUMNS) + ",analyzed_at) VALUES ("
               + ",".join(["?"] * (len(_COLUMNS) + 1)) + ")")


class AnalyzerDB:
    def __init__(self, path: str):
        self.path = path

    def _connect(self):
        os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
        conn = sqlite3.connect(self.path, timeout=30)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.row_factory = sqlite3.Row
        return conn

    def init_schema(self):
        conn = self._connect()
        try:
            conn.executescript(_SCHEMA)
            conn.commit()
        finally:
            conn.close()

    def analyzed_paths(self):
        conn = self._connect()
        try:
            return {r[0] for r in conn.execute("SELECT file_path FROM track_analysis").fetchall()}
        finally:
            conn.close()

    def count(self) -> int:
        conn = self._connect()
        try:
            return conn.execute("SELECT COUNT(*) FROM track_analysis").fetchone()[0]
        finally:
            conn.close()

    def save_batch(self, records):
        """INSERT OR REPLACE each record. Missing text fields default to '', numerics to 0."""
        now = time.time()
        rows = [
            tuple(r.get(c, "" if c in _TEXT_COLS else 0) for c in _COLUMNS) + (now,)
            for r in records
        ]
        conn = self._connect()
        try:
            conn.executemany(_INSERT_SQL, rows)
            conn.commit()
        finally:
            conn.close()
