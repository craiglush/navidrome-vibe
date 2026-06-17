"""History of vibe requests (single-user). SQLite, no thread-locals.
All queries use parameterized placeholders — no string-built SQL.
"""

import json
import os
import sqlite3
import time

_SCHEMA = """
CREATE TABLE IF NOT EXISTS vibe_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prompt TEXT NOT NULL,
    provider TEXT NOT NULL DEFAULT 'ollama',
    ranges_json TEXT,
    reasoning TEXT,
    track_count INTEGER DEFAULT 0,
    playlist_id TEXT,
    playlist_name TEXT,
    created_at REAL
);
"""


class VibeHistory:
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

    def save(self, *, prompt, provider, ranges, reasoning,
             playlist_id, playlist_name, track_count):
        conn = self._connect()
        try:
            conn.execute(
                """INSERT INTO vibe_history
                   (prompt, provider, ranges_json, reasoning, track_count,
                    playlist_id, playlist_name, created_at)
                   VALUES (?,?,?,?,?,?,?,?)""",
                (prompt, provider, json.dumps(ranges), reasoning, track_count,
                 playlist_id, playlist_name, time.time()),
            )
            conn.commit()
        finally:
            conn.close()

    def recent(self, limit=20):
        conn = self._connect()
        try:
            rows = conn.execute(
                "SELECT * FROM vibe_history ORDER BY created_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
            out = []
            for r in rows:
                d = dict(r)
                d["ranges"] = json.loads(d.pop("ranges_json") or "{}")
                out.append(d)
            return out
        finally:
            conn.close()

    def delete(self, entry_id):
        conn = self._connect()
        try:
            conn.execute("DELETE FROM vibe_history WHERE id = ?", (entry_id,))
            conn.commit()
        finally:
            conn.close()
