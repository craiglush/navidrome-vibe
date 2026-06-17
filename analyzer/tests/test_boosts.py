from boosts import apply_context_boosts


def test_genre_boost_applied():
    out = apply_context_boosts({"danceability": 0.2, "mood_party": 0.1}, "Drum & Bass", 0)
    assert out["danceability"] > 0.2
    assert out["mood_party"] > 0.1


def test_bpm_dnb_halftime_doubled_then_boosted():
    out = apply_context_boosts({"danceability": 0.3}, "dnb", 86)
    assert out["danceability"] >= 0.5


def test_scores_clamped_0_1():
    out = apply_context_boosts({"mood_aggressive": 0.95}, "metal", 0)
    assert 0.0 <= out["mood_aggressive"] <= 1.0


def test_unknown_genre_no_change():
    out = apply_context_boosts({"danceability": 0.4}, "spoken word", 0)
    assert out["danceability"] == 0.4
