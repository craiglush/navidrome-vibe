import server as server_mod


def _app(cfg, monkeypatch, fake_result=None):
    def fake_generate(scenario, *, cfg, analysis_db, client, count=30,
                      excluded_genres=None, progress_cb=None):
        return fake_result or {"playlist_id": "p1", "playlist_name": "Vibe",
                               "track_count": 3, "reasoning": "r", "ranges": {},
                               "tracks": [], "starred_count": 0}
    monkeypatch.setattr(server_mod, "generate_vibe_playlist", fake_generate)
    app = server_mod.create_app(cfg)
    app.config.update(TESTING=True)
    return app.test_client()


def test_healthz(cfg, monkeypatch):
    client = _app(cfg, monkeypatch)
    assert client.get("/healthz").status_code == 200


def test_vibe_requires_prompt(cfg, monkeypatch):
    client = _app(cfg, monkeypatch)
    resp = client.post("/api/vibe", json={})
    assert resp.status_code == 400


def test_vibe_happy_path(cfg, monkeypatch):
    client = _app(cfg, monkeypatch)
    resp = client.post("/api/vibe", json={"prompt": "rainy day", "count": 10})
    assert resp.status_code == 200
    assert resp.get_json()["playlist_name"] == "Vibe"


def test_vibe_auth_enforced_when_token_set(cfg, monkeypatch):
    cfg.api_token = "secret-token"
    client = _app(cfg, monkeypatch)
    assert client.post("/api/vibe", json={"prompt": "x"}).status_code == 401
    ok = client.post("/api/vibe", json={"prompt": "x"},
                     headers={"Authorization": "Bearer secret-token"})
    assert ok.status_code == 200


def test_index_served(cfg, monkeypatch):
    client = _app(cfg, monkeypatch)
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"vibe" in resp.data.lower()


def test_vibe_rejects_non_integer_count(cfg, monkeypatch):
    client = _app(cfg, monkeypatch)
    resp = client.post("/api/vibe", json={"prompt": "x", "count": "abc"})
    assert resp.status_code == 400


def test_vibe_rejects_zero_count(cfg, monkeypatch):
    client = _app(cfg, monkeypatch)
    resp = client.post("/api/vibe", json={"prompt": "x", "count": 0})
    assert resp.status_code == 400


def test_vibe_value_error_is_422(cfg, monkeypatch):
    import server as server_mod
    def boom(scenario, *, cfg, analysis_db, client, count=30,
             excluded_genres=None, progress_cb=None):
        raise ValueError("LLM returned no valid feature ranges")
    monkeypatch.setattr(server_mod, "generate_vibe_playlist", boom)
    app = server_mod.create_app(cfg)
    app.config.update(TESTING=True)
    resp = app.test_client().post("/api/vibe", json={"prompt": "x"})
    assert resp.status_code == 422
    assert "valid feature ranges" in resp.get_json()["error"]


def test_vibe_generic_error_is_500_without_leak(cfg, monkeypatch):
    import server as server_mod
    def boom(scenario, *, cfg, analysis_db, client, count=30,
             excluded_genres=None, progress_cb=None):
        raise KeyError("secret-internal-detail")
    monkeypatch.setattr(server_mod, "generate_vibe_playlist", boom)
    app = server_mod.create_app(cfg)
    app.config.update(TESTING=True)
    resp = app.test_client().post("/api/vibe", json={"prompt": "x"})
    assert resp.status_code == 500
    assert "secret-internal-detail" not in resp.get_data(as_text=True)


def test_history_failure_does_not_fail_request(cfg, monkeypatch):
    import server as server_mod
    monkeypatch.setattr(server_mod.VibeHistory, "save",
                        lambda *a, **k: (_ for _ in ()).throw(Exception("db boom")))
    client = _app(cfg, monkeypatch)
    resp = client.post("/api/vibe", json={"prompt": "rainy day"})
    assert resp.status_code == 200


def test_vibe_async_returns_202_and_runs_in_background(cfg, monkeypatch):
    import threading
    done = threading.Event()
    calls = []

    def fake_generate(scenario, *, cfg, analysis_db, client, count=30,
                      excluded_genres=None, progress_cb=None):
        calls.append(scenario)
        done.set()
        return {"playlist_id": "p", "playlist_name": "V", "track_count": 1,
                "reasoning": "", "ranges": {}, "tracks": [], "starred_count": 0}

    monkeypatch.setattr(server_mod, "generate_vibe_playlist", fake_generate)
    app = server_mod.create_app(cfg)
    app.config.update(TESTING=True)
    client = app.test_client()

    resp = client.post("/api/vibe", json={"prompt": "rainy", "async": True})
    assert resp.status_code == 202
    assert resp.get_json()["status"] == "accepted"
    assert done.wait(timeout=5), "background generation did not run"
    assert calls == ["rainy"]
