def _rec(path, title="T", artist="A", **kw):
    base = {"file_path": path, "title": title, "artist": artist, "album": "Al",
            "bpm": 120, "danceability": 0.5, "mood_happy": 0.5, "mood_sad": 0.1,
            "mood_relaxed": 0.3, "mood_aggressive": 0.1, "mood_party": 0.4,
            "energy": 0.5, "genre": "Pop", "genre_normalized": "pop",
            "arousal": 0.0, "valence": 0.0}
    base.update(kw)
    return base


def test_init_save_and_count(tmp_path):
    from db import AnalyzerDB
    db = AnalyzerDB(str(tmp_path / "analysis.db"))
    db.init_schema()
    db.save_batch([_rec("/m/a.flac"), _rec("/m/b.flac")])
    assert db.count() == 2


def test_analyzed_paths(tmp_path):
    from db import AnalyzerDB
    db = AnalyzerDB(str(tmp_path / "analysis.db"))
    db.init_schema()
    db.save_batch([_rec("/m/a.flac")])
    assert db.analyzed_paths() == {"/m/a.flac"}


def test_save_batch_is_idempotent(tmp_path):
    from db import AnalyzerDB
    db = AnalyzerDB(str(tmp_path / "analysis.db"))
    db.init_schema()
    db.save_batch([_rec("/m/a.flac", title="First")])
    db.save_batch([_rec("/m/a.flac", title="Second")])
    assert db.count() == 1


def test_schema_matches_app(tmp_path):
    import sqlite3
    from db import AnalyzerDB
    db = AnalyzerDB(str(tmp_path / "analysis.db"))
    db.init_schema()
    conn = sqlite3.connect(db.path)
    cols = {r[1] for r in conn.execute("PRAGMA table_info(track_analysis)").fetchall()}
    conn.close()
    expected = {"id", "file_path", "title", "artist", "album", "bpm", "danceability",
                "mood_happy", "mood_sad", "mood_relaxed", "mood_aggressive", "mood_party",
                "energy", "analyzed_at", "genre", "genre_normalized", "arousal", "valence"}
    assert cols == expected
