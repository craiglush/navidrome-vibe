from vibe.scoring import score_tracks, normalize_key, boost_starred


def _tracks():
    return [
        {"file_path": "/m/a", "title": "A", "artist": "X", "mood_relaxed": 0.9,
         "energy": 0.1, "genre": "Ambient"},
        {"file_path": "/m/b", "title": "B", "artist": "Y", "mood_relaxed": 0.1,
         "energy": 0.9, "genre": "Dance"},
    ]


def test_score_prefers_in_range_track():
    ranges = {"mood_relaxed": [0.6, 1.0], "energy": [0.0, 0.3]}
    scored = score_tracks(_tracks(), ranges)
    by_path = {s["track"]["file_path"]: s["score"] for s in scored}
    assert by_path["/m/a"] > by_path["/m/b"]


def test_score_skips_tracks_with_no_features():
    ranges = {"mood_relaxed": [0.6, 1.0]}
    tracks = [{"file_path": "/m/z", "title": "Z", "artist": "Q"}]
    assert score_tracks(tracks, ranges) == []


def test_excluded_genres_filtered_out():
    ranges = {"energy": [0.0, 1.0]}
    scored = score_tracks(_tracks(), ranges, excluded_genres=["dance"])
    paths = {s["track"]["file_path"] for s in scored}
    assert paths == {"/m/a"}


def test_normalize_key():
    assert normalize_key("  Hello ", "World") == "world||hello"


def test_boost_starred_multiplies():
    scored = [{"track": {"file_path": "/m/a"}, "score": 0.5}]
    nd_id_map = {"/m/a": "song-1"}
    boost_starred(scored, {"song-1"}, nd_id_map)
    assert abs(scored[0]["score"] - 0.75) < 1e-9
