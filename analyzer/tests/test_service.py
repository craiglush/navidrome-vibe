import service as service_mod
from fastapi.testclient import TestClient
from config import AnalyzerConfig


def _cfg(tmp_path):
    return AnalyzerConfig(
        music_root=str(tmp_path / "music"),
        analysis_db_path=str(tmp_path / "analysis.db"),
        models_dir=str(tmp_path / "models"),
        scan_on_start=False, scan_interval_hours=0, batch_size=4, port=8000)


def test_health_ok(tmp_path):
    app = service_mod.create_app(_cfg(tmp_path))
    c = TestClient(app)
    r = c.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
    assert "analyzed_tracks" in r.json()


def test_analyze_file_uses_backend(tmp_path, monkeypatch):
    monkeypatch.setattr(service_mod, "analyze_file",
        lambda path, models_dir: {"file_path": path, "title": "X", "bpm": 120})
    app = service_mod.create_app(_cfg(tmp_path))
    c = TestClient(app)
    import os
    os.makedirs(str(tmp_path / "music"), exist_ok=True)
    f = tmp_path / "music" / "x.flac"
    f.write_bytes(b"\x00")
    r = c.post("/api/analysis/file", json={"file_path": str(f)})
    assert r.status_code == 200
    assert r.json()["title"] == "X"


def test_analyze_file_rejects_path_outside_music_root(tmp_path, monkeypatch):
    monkeypatch.setattr(service_mod, "analyze_file",
        lambda path, models_dir: {"file_path": path})
    app = service_mod.create_app(_cfg(tmp_path))
    c = TestClient(app)
    r = c.post("/api/analysis/file", json={"file_path": "/etc/passwd"})
    assert r.status_code == 400


def test_scan_triggers_and_reports_status(tmp_path, monkeypatch):
    monkeypatch.setattr(service_mod, "scan_library",
        lambda music_root, db, **kw: {"analyzed": 3, "failed": 0, "pending_total": 3})
    app = service_mod.create_app(_cfg(tmp_path))
    c = TestClient(app)
    r = c.post("/api/scan")
    assert r.status_code in (200, 202)
    s = c.get("/api/scan/status")
    assert s.status_code == 200
    assert "scanning" in s.json()
