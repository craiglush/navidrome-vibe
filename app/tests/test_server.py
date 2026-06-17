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
