"""CLI: `python -m analyzer scan` runs a one-shot library scan and exits."""

import sys

from config import AnalyzerConfig
from db import AnalyzerDB
from essentia_backend import analyze_file
from scanner import scan_library


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    cmd = argv[0] if argv else "scan"
    if cmd != "scan":
        print(f"unknown command: {cmd}; usage: python -m analyzer scan")
        return 2
    cfg = AnalyzerConfig.from_env()
    db = AnalyzerDB(cfg.analysis_db_path)
    db.init_schema()
    result = scan_library(cfg.music_root, db,
                          analyze_fn=lambda p: analyze_file(p, cfg.models_dir),
                          batch_size=cfg.batch_size, progress_cb=print)
    print(f"done: {result}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
