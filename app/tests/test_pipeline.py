import vibe.pipeline as pipeline


class FakeClient:
    def __init__(self):
        self.created = None
    def get_all_songs(self):
        return [
            {"id": "nd-a", "title": "Calm One", "artist": "Artist A"},
            {"id": "nd-b", "title": "Party Two", "artist": "Artist B"},
            {"id": "nd-c", "title": "Sad Three", "artist": "Artist C"},
        ]
    def get_starred(self):
        return [{"id": "nd-a"}]
    def get_playlists(self):
        return []
    def delete_playlist(self, pid):
        pass
    def create_playlist(self, name, song_ids):
        self.created = (name, song_ids)
        return "pl-new"


def test_generate_vibe_playlist_happy_path(cfg, analysis_db, monkeypatch):
    monkeypatch.setattr(pipeline, "interpret_scenario",
        lambda scenario, c: '{"ranges": {"mood_relaxed": [0.6, 1.0], "energy": [0.0, 0.3]}, "reasoning": "calm vibes"}')
    monkeypatch.setattr(pipeline, "generate_title", lambda desc, c: "Calm Vibes")

    client = FakeClient()
    result = pipeline.generate_vibe_playlist(
        "quiet evening", cfg=cfg, analysis_db=analysis_db, client=client, count=10)

    assert result["playlist_id"] == "pl-new"
    assert result["playlist_name"] == "Calm Vibes"
    assert result["reasoning"] == "calm vibes"
    assert result["track_count"] >= 1
    assert "nd-a" in client.created[1]
    assert result["starred_count"] >= 1


def test_generate_raises_when_no_analyzed_tracks(cfg, tmp_path, monkeypatch):
    from vibe.analysis_db import AnalysisDB
    empty = AnalysisDB(str(tmp_path / "empty.db"))
    empty.init_schema()
    monkeypatch.setattr(pipeline, "interpret_scenario",
        lambda s, c: '{"ranges": {"energy": [0,1]}, "reasoning": ""}')
    client = FakeClient()
    try:
        pipeline.generate_vibe_playlist("x", cfg=cfg, analysis_db=empty,
                                        client=client, count=5)
        assert False, "expected RuntimeError"
    except RuntimeError as e:
        assert "analyzed" in str(e).lower()


def test_generate_deletes_existing_same_name_playlist(cfg, analysis_db, monkeypatch):
    monkeypatch.setattr(pipeline, "interpret_scenario",
        lambda s, c: '{"ranges": {"mood_relaxed": [0.6, 1.0]}, "reasoning": "calm"}')
    monkeypatch.setattr(pipeline, "generate_title", lambda d, c: "Calm Vibes")

    deleted = []

    class ClientWithDup:
        def get_all_songs(self):
            return [{"id": "nd-a", "title": "Calm One", "artist": "Artist A"}]
        def get_starred(self):
            return []
        def get_playlists(self):
            return [{"id": "old-1", "name": "Calm Vibes"}]
        def delete_playlist(self, pid):
            deleted.append(pid)
        def create_playlist(self, name, song_ids):
            return "pl-new"

    pipeline.generate_vibe_playlist("quiet", cfg=cfg, analysis_db=analysis_db,
                                    client=ClientWithDup(), count=5)
    assert "old-1" in deleted
