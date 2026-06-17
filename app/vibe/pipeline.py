"""Vibe playlist orchestrator: scenario -> ranges -> scored tracks -> playlist.

Dependencies (cfg, analysis_db, client) are injected so this is unit-testable
with no network and no global state.
"""

import json
import logging

from vibe.features import parse_llm_response
from vibe.llm import generate_title, interpret_scenario
from vibe.scoring import boost_starred, score_tracks

log = logging.getLogger(__name__)


def _build_id_map(client, scored_items, max_needed):
    """Map analysis tracks -> Subsonic song ids via per-track search3.

    Bounded by candidate count, NOT library size, so it scales to large
    libraries (fetching the whole library per request does not). Stops once
    max_needed tracks are mapped.
    """
    id_map = {}
    for item in scored_items:
        if len(id_map) >= max_needed:
            break
        t = item["track"]
        query = (t.get("title", "") + " " + t.get("artist", "")).strip()
        if not query:
            continue
        try:
            res = client.search(query, song_count=3)
        except Exception as e:
            log.warning("search failed for %r: %s", query, e)
            continue
        if res:
            id_map[t["file_path"]] = res[0]["id"]
    return id_map


def generate_vibe_playlist(scenario, *, cfg, analysis_db, client,
                           count=30, excluded_genres=None, progress_cb=None):
    """Full pipeline. Returns a dict describing the created playlist."""
    def progress(msg):
        if progress_cb:
            progress_cb(msg)
        log.info(msg)

    # 1. LLM -> ranges
    progress('Asking ' + cfg.llm_provider + ' to interpret: "' + scenario + '"...')
    raw = interpret_scenario(scenario, cfg)
    ranges, reasoning = parse_llm_response(raw)
    progress("AI reasoning: " + reasoning)
    log.info("Score ranges: %s", json.dumps(ranges))

    # 2. Load analyzed tracks
    progress("Loading your music library analysis...")
    tracks = analysis_db.all_tracks()
    if not tracks:
        raise RuntimeError("No analyzed tracks found. Run audio analysis first.")

    # 3. Score
    progress("Scoring " + str(len(tracks)) + " tracks against target ranges...")
    scored = score_tracks(tracks, ranges, excluded_genres=excluded_genres)
    if not scored:
        raise RuntimeError("No tracks matched the target ranges and genre filter.")
    scored.sort(key=lambda x: x["score"], reverse=True)
    top = scored[: count * 3]

    # 4. Match to Subsonic ids
    progress("Matching tracks to your Navidrome library...")
    id_map = _build_id_map(client, top, count * 2)

    # 5. Starred boost
    starred_ids = set()
    try:
        starred_ids = {s["id"] for s in client.get_starred()}
    except Exception as e:
        log.warning("Could not fetch starred songs: %s", e)
    if starred_ids:
        boost_starred(top, starred_ids, id_map)
        top.sort(key=lambda x: x["score"], reverse=True)

    # 6. Select top N unique
    selected, seen = [], set()
    for item in top:
        nd_id = id_map.get(item["track"]["file_path"])
        if nd_id and nd_id not in seen:
            seen.add(nd_id)
            selected.append({
                "navidrome_id": nd_id,
                "title": item["track"].get("title", ""),
                "artist": item["track"].get("artist", ""),
                "score": round(item["score"], 3),
                "starred": nd_id in starred_ids,
            })
        if len(selected) >= count:
            break
    if not selected:
        raise RuntimeError("Could not match scored tracks to Navidrome. Is the library scanned?")

    # 7. Title + create (replace existing same-name playlist)
    progress("Generating playlist title...")
    name = generate_title(scenario, cfg)
    song_ids = [t["navidrome_id"] for t in selected]
    try:
        for pl in client.get_playlists():
            if pl.get("name") == name:
                client.delete_playlist(pl["id"])
                break
    except Exception as e:
        log.warning("could not check/delete existing playlist: %s", e)
    progress("Creating playlist with " + str(len(selected)) + " tracks...")
    playlist_id = client.create_playlist(name, song_ids)
    progress('Playlist "' + name + '" created (' + str(len(selected)) + ' tracks)')

    return {
        "playlist_id": playlist_id,
        "playlist_name": name,
        "track_count": len(selected),
        "reasoning": reasoning,
        "ranges": ranges,
        "tracks": selected[:10],
        "starred_count": sum(1 for t in selected if t["starred"]),
    }
