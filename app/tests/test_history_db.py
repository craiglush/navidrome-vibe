def test_save_and_recent(tmp_path):
    from vibe.history_db import VibeHistory
    h = VibeHistory(str(tmp_path / "vibe.db"))
    h.init_schema()
    h.save(prompt="rainy day", provider="ollama",
            ranges={"energy": [0.0, 0.2]}, reasoning="calm",
            playlist_id="p1", playlist_name="Rainy Calm", track_count=12)
    rows = h.recent()
    assert len(rows) == 1
    assert rows[0]["prompt"] == "rainy day"
    assert rows[0]["ranges"] == {"energy": [0.0, 0.2]}
    assert rows[0]["playlist_name"] == "Rainy Calm"


def test_delete(tmp_path):
    from vibe.history_db import VibeHistory
    h = VibeHistory(str(tmp_path / "vibe.db"))
    h.init_schema()
    h.save(prompt="x", provider="ollama", ranges={}, reasoning="",
            playlist_id="p", playlist_name="X", track_count=1)
    entry_id = h.recent()[0]["id"]
    h.delete(entry_id)
    assert h.recent() == []
