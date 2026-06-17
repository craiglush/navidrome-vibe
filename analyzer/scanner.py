"""Walk a music library, analyze new files via an injected analyze_fn, batch-write the DB."""

import logging
import os

log = logging.getLogger(__name__)

AUDIO_EXTENSIONS = {".m4a", ".mp3", ".flac", ".ogg", ".opus", ".wav"}


def find_audio_files(music_root):
    """Return sorted absolute paths of audio files under music_root (deterministic)."""
    found = []
    for dirpath, _dirs, files in os.walk(music_root):
        for name in files:
            if os.path.splitext(name)[1].lower() in AUDIO_EXTENSIONS:
                found.append(os.path.join(dirpath, name))
    found.sort()
    return found


def scan_library(music_root, db, *, analyze_fn, batch_size=16, limit=None, progress_cb=None):
    """Analyze every not-yet-analyzed audio file under music_root and write to db.

    analyze_fn(path) -> record dict (must include 'file_path' + feature fields).
    Returns {"analyzed": int, "failed": int, "pending_total": int}.
    """
    def progress(msg):
        if progress_cb:
            progress_cb(msg)
        log.info(msg)

    already = db.analyzed_paths()
    pending = [p for p in find_audio_files(music_root) if p not in already]
    if limit is not None:
        pending = pending[:limit]
    progress(f"{len(pending)} files to analyze")

    analyzed = 0
    failed = 0
    batch = []
    for path in pending:
        try:
            rec = analyze_fn(path)
        except Exception as e:
            failed += 1
            log.warning("analysis failed for %s: %s", path, e)
            continue
        batch.append(rec)
        if len(batch) >= batch_size:
            db.save_batch(batch)
            analyzed += len(batch)
            batch = []
            progress(f"analyzed {analyzed}/{len(pending)}")
    if batch:
        db.save_batch(batch)
        analyzed += len(batch)

    progress(f"scan complete: {analyzed} analyzed, {failed} failed")
    return {"analyzed": analyzed, "failed": failed, "pending_total": len(pending)}
