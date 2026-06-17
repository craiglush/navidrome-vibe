import sqlite3
import pytest
from vibe.config import Config


@pytest.fixture
def cfg(tmp_path):
    return Config(
        navidrome_url="http://nd.test",
        navidrome_user="tester",
        navidrome_password="pw",
        analysis_db_path=str(tmp_path / "analysis.db"),
        vibe_db_path=str(tmp_path / "vibe.db"),
        llm_provider="ollama",
        ollama_url="http://ollama.test",
        ollama_model="qwen2.5:7b",
        ollama_think=False,
        ollama_num_ctx=8192,
        openai_base_url="http://owui.test",
        openai_api_key="owui-key",
        openai_model="some-model",
        anthropic_api_key="ak-test",
        anthropic_model="claude-haiku-4-5",
        api_token="",
        port=4546,
    )


@pytest.fixture
def analysis_db(tmp_path):
    """A populated track_analysis DB with three rows for pipeline tests."""
    from vibe.analysis_db import AnalysisDB
    db = AnalysisDB(str(tmp_path / "analysis.db"))
    db.init_schema()
    conn = sqlite3.connect(db.path)
    conn.executemany(
        """INSERT INTO track_analysis
           (file_path,title,artist,album,bpm,danceability,mood_happy,mood_sad,
            mood_relaxed,mood_aggressive,mood_party,energy,genre,genre_normalized,
            arousal,valence,analyzed_at)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        [
            ("/music/a.flac", "Calm One", "Artist A", "Album A", 70, 0.2,
             0.3, 0.2, 0.9, 0.05, 0.1, 0.1, "Ambient", "ambient", 0.2, 0.4, 1.0),
            ("/music/b.flac", "Party Two", "Artist B", "Album B", 128, 0.9,
             0.8, 0.05, 0.1, 0.2, 0.9, 0.8, "Dance", "dance", 0.9, 0.8, 1.0),
            ("/music/c.flac", "Sad Three", "Artist C", "Album C", 80, 0.3,
             0.1, 0.9, 0.4, 0.1, 0.05, 0.2, "Blues", "blues", 0.3, 0.2, 1.0),
        ],
    )
    conn.commit()
    conn.close()
    return db
