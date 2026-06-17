"""FastAPI service: health, on-demand single-file analysis, and background library scan."""

import logging
import os
import threading

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from config import AnalyzerConfig
from db import AnalyzerDB
from essentia_backend import analyze_file
from scanner import scan_library

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class AnalyzeRequest(BaseModel):
    file_path: str


def create_app(cfg: AnalyzerConfig = None) -> FastAPI:
    cfg = cfg or AnalyzerConfig.from_env()
    app = FastAPI(title="Vibe Analyzer", version="1.0.0")
    db = AnalyzerDB(cfg.analysis_db_path)
    db.init_schema()

    state = {"scanning": False, "last_result": None}
    lock = threading.Lock()

    def _run_scan():
        try:
            state["last_result"] = scan_library(
                cfg.music_root, db,
                analyze_fn=lambda p: analyze_file(p, cfg.models_dir),
                batch_size=cfg.batch_size)
        except Exception:
            log.exception("scan failed")
        finally:
            with lock:
                state["scanning"] = False

    def _start_scan():
        with lock:
            if state["scanning"]:
                return False
            state["scanning"] = True
        threading.Thread(target=_run_scan, daemon=True).start()
        return True

    @app.get("/health")
    def health():
        return {"status": "ok", "analyzed_tracks": db.count(), "scanning": state["scanning"]}

    @app.post("/api/analysis/file")
    def analysis_file(req: AnalyzeRequest):
        music_root = os.path.abspath(cfg.music_root)
        requested = os.path.abspath(req.file_path)
        if requested != music_root and not requested.startswith(music_root + os.sep):
            raise HTTPException(status_code=400, detail="file must be within MUSIC_ROOT")
        if not os.path.exists(requested):
            raise HTTPException(status_code=404, detail="file not found")
        return analyze_file(requested, cfg.models_dir)

    @app.post("/api/scan", status_code=202)
    def scan():
        started = _start_scan()
        return {"started": started, "scanning": state["scanning"]}

    @app.get("/api/scan/status")
    def scan_status():
        return {"scanning": state["scanning"], "last_result": state["last_result"],
                "analyzed_tracks": db.count()}

    if cfg.scan_on_start:
        _start_scan()

    return app


if __name__ == "__main__":
    import uvicorn
    _cfg = AnalyzerConfig.from_env()
    uvicorn.run(create_app(_cfg), host="0.0.0.0", port=_cfg.port)
