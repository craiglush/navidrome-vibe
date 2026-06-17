"""Environment-driven configuration for the analyzer service."""

import os
from dataclasses import dataclass


def _bool(name: str, default: bool) -> bool:
    v = os.environ.get(name)
    if v is None:
        return default
    return v.strip().lower() in ("1", "true", "yes", "on")


@dataclass
class AnalyzerConfig:
    music_root: str
    analysis_db_path: str
    models_dir: str
    scan_on_start: bool
    scan_interval_hours: float
    batch_size: int
    port: int

    @classmethod
    def from_env(cls) -> "AnalyzerConfig":
        return cls(
            music_root=os.environ.get("MUSIC_ROOT", "/music"),
            analysis_db_path=os.environ.get("ANALYSIS_DB_PATH", "/data/analysis.db"),
            models_dir=os.environ.get("MODELS_DIR", "/app/models"),
            scan_on_start=_bool("SCAN_ON_START", True),
            scan_interval_hours=float(os.environ.get("SCAN_INTERVAL_HOURS", "0")),
            batch_size=int(os.environ.get("BATCH_SIZE", "16")),
            port=int(os.environ.get("ANALYZER_PORT", "8000")),
        )
