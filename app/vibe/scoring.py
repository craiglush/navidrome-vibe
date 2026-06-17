"""Scoring analyzed tracks against LLM-produced feature ranges. Pure module."""

STARRED_BOOST = 1.5


def score_tracks(tracks, ranges, excluded_genres=None):
    """Score each track 0..1 by how well its features fit the target ranges.

    Returns list of {"track": dict, "score": float}, unsorted.
    Tracks with none of the ranged features present are skipped.
    """
    excluded = [g.lower() for g in (excluded_genres or []) if g.strip()]
    scored = []

    for track in tracks:
        if excluded:
            tg = (track.get("genre_normalized") or track.get("genre") or "").lower()
            if any(g in tg for g in excluded):
                continue

        total = 0.0
        n = 0
        for feature, (lo, hi) in ranges.items():
            val = track.get(feature)
            if val is None:
                continue
            val = float(val)
            n += 1
            if lo <= val <= hi:
                span = hi - lo
                if span > 0:
                    center = (lo + hi) / 2
                    closeness = 1.0 - abs(val - center) / (span / 2)
                    total += 0.8 + 0.2 * closeness
                else:
                    total += 1.0
            else:
                dist = min(abs(val - lo), abs(val - hi))
                total += max(0.0, 1.0 - dist * 3)

        if n == 0:
            continue
        scored.append({"track": track, "score": total / n})

    return scored


def normalize_key(title, artist):
    """Lookup key to match analysis tracks to Subsonic songs."""
    t = (title or "").strip().lower()
    a = (artist or "").strip().lower()
    return f"{a}||{t}"


def boost_starred(scored_tracks, starred_ids, nd_id_map):
    """Multiply score by STARRED_BOOST for tracks whose Subsonic id is starred.

    nd_id_map maps file_path -> subsonic song id. Mutates scored_tracks in place.
    """
    for item in scored_tracks:
        nd_id = nd_id_map.get(item["track"]["file_path"])
        if nd_id and nd_id in starred_ids:
            item["score"] *= STARRED_BOOST
    return scored_tracks
