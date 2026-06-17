import os
from db import AnalyzerDB
from scanner import find_audio_files, scan_library


def _make_audio(tmp_path, names):
    for n in names:
        p = tmp_path / n
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(b"\x00")
    return str(tmp_path)


def _fake_analyze(path):
    return {"file_path": path, "title": os.path.basename(path), "artist": "A",
            "album": "Al", "bpm": 120, "danceability": 0.5, "mood_happy": 0.5,
            "mood_sad": 0.1, "mood_relaxed": 0.3, "mood_aggressive": 0.1,
            "mood_party": 0.4, "energy": 0.5, "genre": "Pop",
            "genre_normalized": "pop", "arousal": 0.0, "valence": 0.0}


def test_find_audio_files_filters_extensions(tmp_path):
    root = _make_audio(tmp_path, ["a.flac", "b.mp3", "c.txt", "sub/d.m4a"])
    found = set(os.path.basename(p) for p in find_audio_files(root))
    assert found == {"a.flac", "b.mp3", "d.m4a"}


def test_scan_writes_all_and_reports(tmp_path):
    root = _make_audio(tmp_path / "music", ["a.flac", "b.mp3"])
    db = AnalyzerDB(str(tmp_path / "analysis.db"))
    db.init_schema()
    result = scan_library(root, db, analyze_fn=_fake_analyze, batch_size=1)
    assert result["analyzed"] == 2
    assert db.count() == 2


def test_scan_skips_already_analyzed(tmp_path):
    root = _make_audio(tmp_path / "music", ["a.flac", "b.mp3"])
    db = AnalyzerDB(str(tmp_path / "analysis.db"))
    db.init_schema()
    scan_library(root, db, analyze_fn=_fake_analyze)
    result = scan_library(root, db, analyze_fn=_fake_analyze)
    assert result["analyzed"] == 0


def test_scan_continues_past_analyze_errors(tmp_path):
    root = _make_audio(tmp_path / "music", ["good.flac", "bad.mp3"])
    db = AnalyzerDB(str(tmp_path / "analysis.db"))
    db.init_schema()

    def flaky(path):
        if path.endswith("bad.mp3"):
            raise RuntimeError("boom")
        return _fake_analyze(path)

    result = scan_library(root, db, analyze_fn=flaky)
    assert result["analyzed"] == 1
    assert result["failed"] == 1


def test_scan_respects_limit(tmp_path):
    root = _make_audio(tmp_path / "music", ["a.flac", "b.mp3", "c.flac"])
    db = AnalyzerDB(str(tmp_path / "analysis.db"))
    db.init_schema()
    result = scan_library(root, db, analyze_fn=_fake_analyze, limit=2)
    assert result["analyzed"] == 2
