"""Genre/BPM context boosts applied to raw essentia scores. Pure module."""

GENRE_BOOSTS = {
    "drum": {"danceability": 0.35, "mood_party": 0.15, "mood_aggressive": 0.10},
    "jungle": {"danceability": 0.35, "mood_party": 0.15, "mood_aggressive": 0.10},
    "dnb": {"danceability": 0.35, "mood_party": 0.15, "mood_aggressive": 0.10},
    "dance": {"danceability": 0.20, "mood_party": 0.10},
    "house": {"danceability": 0.20, "mood_party": 0.10},
    "techno": {"danceability": 0.25, "mood_party": 0.15, "mood_aggressive": 0.10},
    "trance": {"danceability": 0.20, "mood_party": 0.10, "mood_happy": 0.10},
    "edm": {"danceability": 0.20, "mood_party": 0.10},
    "electronic": {"danceability": 0.10, "mood_party": 0.05},
    "disco": {"danceability": 0.20, "mood_party": 0.15, "mood_happy": 0.10},
    "funk": {"danceability": 0.15, "mood_party": 0.10, "mood_happy": 0.05},
    "metal": {"mood_aggressive": 0.25, "mood_relaxed": -0.15},
    "hardcore": {"mood_aggressive": 0.25, "danceability": 0.15},
    "punk": {"mood_aggressive": 0.15, "mood_party": 0.05},
    "industrial": {"mood_aggressive": 0.20},
    "ambient": {"mood_relaxed": 0.20, "mood_aggressive": -0.10},
    "downtempo": {"mood_relaxed": 0.15, "danceability": -0.10},
    "chillout": {"mood_relaxed": 0.20, "mood_party": -0.10},
    "lounge": {"mood_relaxed": 0.15},
    "easy listening": {"mood_relaxed": 0.20, "mood_happy": 0.10},
    "new age": {"mood_relaxed": 0.20},
    "blues": {"mood_sad": 0.10},
    "emo": {"mood_sad": 0.15, "mood_aggressive": 0.05},
    "reggae": {"mood_happy": 0.10, "mood_relaxed": 0.10},
    "ska": {"mood_happy": 0.15, "danceability": 0.10},
    "pop": {"mood_happy": 0.05, "danceability": 0.05},
    "r&b": {"mood_relaxed": 0.05, "mood_party": 0.05},
    "soul": {"mood_relaxed": 0.05, "mood_happy": 0.05},
}

BPM_DANCEABILITY_BOOST = {
    (140, 180): 0.20,
    (180, 250): 0.15,
    (90, 110): 0.05,
}


def apply_context_boosts(scores, genre, bpm):
    """Adjust raw essentia scores using genre/BPM context. Returns a new dict, clamped 0..1."""
    adjusted = dict(scores)
    genre_lower = (genre or "").lower()

    for keyword, boosts in GENRE_BOOSTS.items():
        if keyword in genre_lower:
            for score_key, boost in boosts.items():
                if score_key in adjusted:
                    adjusted[score_key] = adjusted[score_key] + boost

    if bpm and bpm > 0:
        effective_bpm = bpm
        if 80 <= bpm <= 95 and any(k in genre_lower for k in ("drum", "jungle", "dnb", "bass")):
            effective_bpm = bpm * 2
        for (lo, hi), boost in BPM_DANCEABILITY_BOOST.items():
            if lo <= effective_bpm <= hi:
                adjusted["danceability"] = adjusted.get("danceability", 0) + boost
                break

    for key in adjusted:
        if isinstance(adjusted[key], float):
            adjusted[key] = round(max(0.0, min(1.0, adjusted[key])), 4)
    return adjusted
