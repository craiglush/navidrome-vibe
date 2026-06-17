"""Flask companion app: the interactive 'type your vibe' UI + JSON API."""

import logging
import secrets
import threading
from functools import wraps

from flask import Flask, jsonify, render_template, request

from vibe.analysis_db import AnalysisDB
from vibe.config import Config
from vibe.history_db import VibeHistory
from vibe.pipeline import generate_vibe_playlist
from vibe.subsonic import SubsonicClient

logging.basicConfig(level=logging.INFO)

# Serialize background generations so concurrent async requests (e.g. a plugin
# firing several prompts at once) don't overload the LLM endpoint.
_gen_lock = threading.Lock()


def create_app(cfg: Config = None) -> Flask:
    cfg = cfg or Config.from_env()
    app = Flask(__name__)

    analysis_db = AnalysisDB(cfg.analysis_db_path)
    analysis_db.init_schema()
    history = VibeHistory(cfg.vibe_db_path)
    history.init_schema()

    def require_token(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if cfg.api_token:
                header = request.headers.get("Authorization", "")
                if not secrets.compare_digest(header, "Bearer " + cfg.api_token):
                    return jsonify({"error": "unauthorized"}), 401
            return fn(*args, **kwargs)
        return wrapper

    @app.get("/healthz")
    def healthz():
        return jsonify({"status": "ok", "analyzed_tracks": analysis_db.count()})

    @app.get("/")
    def index():
        return render_template("index.html")

    def _generate_and_save(prompt, count, excluded):
        client = SubsonicClient(cfg.navidrome_url, cfg.navidrome_user, cfg.navidrome_password)
        result = generate_vibe_playlist(
            prompt, cfg=cfg, analysis_db=analysis_db, client=client,
            count=count, excluded_genres=excluded)
        try:
            history.save(prompt=prompt, provider=cfg.llm_provider,
                         ranges=result["ranges"], reasoning=result["reasoning"],
                         playlist_id=result["playlist_id"],
                         playlist_name=result["playlist_name"],
                         track_count=result["track_count"])
        except Exception:
            logging.exception("failed to save vibe history (playlist was still created)")
        return result

    def _run_async(prompt, count, excluded):
        # Serialized so a burst of async prompts runs one at a time.
        with _gen_lock:
            try:
                _generate_and_save(prompt, count, excluded)
            except Exception:
                logging.exception("async vibe generation failed for %r", prompt)

    @app.post("/api/vibe")
    @require_token
    def vibe():
        body = request.get_json(silent=True) or {}
        prompt = (body.get("prompt") or "").strip()
        if not prompt:
            return jsonify({"error": "prompt is required"}), 400
        try:
            count = int(body.get("count", 30))
        except (ValueError, TypeError):
            return jsonify({"error": "count must be an integer"}), 400
        if count < 1:
            return jsonify({"error": "count must be >= 1"}), 400
        excluded = body.get("excluded_genres") or []

        # Async path (used by the scheduled plugin): kick off generation in the
        # background and return immediately, so the caller's request — e.g. a
        # Navidrome scheduler callback with a ~30s deadline — returns instantly.
        if body.get("async"):
            threading.Thread(target=_run_async, args=(prompt, count, excluded),
                             daemon=True).start()
            return jsonify({"status": "accepted", "prompt": prompt}), 202

        try:
            result = _generate_and_save(prompt, count, excluded)
        except (RuntimeError, ValueError) as e:
            return jsonify({"error": str(e)}), 422
        except Exception:
            logging.exception("vibe generation failed")
            return jsonify({"error": "playlist generation failed"}), 500
        return jsonify(result)

    @app.get("/api/vibe/history")
    @require_token
    def vibe_history():
        return jsonify(history.recent())

    @app.delete("/api/vibe/history/<int:entry_id>")
    @require_token
    def delete_history(entry_id):
        history.delete(entry_id)
        return jsonify({"deleted": entry_id})

    return app


# gunicorn uses the app-factory form: `gunicorn "server:create_app()"`.
# We deliberately do NOT instantiate the app at import time, so `import server`
# in tests has no side effects (no /data makedirs, no env-dependent config).
if __name__ == "__main__":
    _cfg = Config.from_env()
    create_app(_cfg).run(host="0.0.0.0", port=_cfg.port)
