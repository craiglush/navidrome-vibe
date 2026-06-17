from config import AnalyzerConfig


def test_defaults(monkeypatch):
    for k in ("MUSIC_ROOT", "ANALYSIS_DB_PATH", "MODELS_DIR", "SCAN_ON_START"):
        monkeypatch.delenv(k, raising=False)
    c = AnalyzerConfig.from_env()
    assert c.music_root == "/music"
    assert c.analysis_db_path == "/data/analysis.db"
    assert c.models_dir == "/app/models"
    assert c.scan_on_start is True
    assert c.batch_size == 16


def test_overrides(monkeypatch):
    monkeypatch.setenv("MUSIC_ROOT", "/m")
    monkeypatch.setenv("SCAN_ON_START", "false")
    monkeypatch.setenv("BATCH_SIZE", "8")
    c = AnalyzerConfig.from_env()
    assert c.music_root == "/m"
    assert c.scan_on_start is False
    assert c.batch_size == 8
