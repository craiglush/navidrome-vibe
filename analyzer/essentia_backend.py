"""Essentia-tensorflow inference for a single audio file. Integration-only.

`essentia` is imported lazily inside analyze_file so the module imports cleanly
on machines without essentia (e.g. for tooling/tests). analyze_file itself requires it.
"""

import logging
import os

import mutagen
import numpy as np

from boosts import apply_context_boosts

log = logging.getLogger(__name__)

_MOOD_MODELS = {
    "mood_happy": "mood_happy-discogs-effnet-1.pb",
    "mood_sad": "mood_sad-discogs-effnet-1.pb",
    "mood_relaxed": "mood_relaxed-discogs-effnet-1.pb",
    "mood_aggressive": "mood_aggressive-discogs-effnet-1.pb",
    "mood_party": "mood_party-discogs-effnet-1.pb",
}
_MOOD_KEYS = list(_MOOD_MODELS) + ["danceability"]


def _read_tags(path):
    title = artist = album = genre = ""
    try:
        tags = mutagen.File(path)
        if tags:
            title = str((tags.get("\xa9nam") or tags.get("title") or [""])[0])
            artist = str((tags.get("\xa9ART") or tags.get("artist") or [""])[0])
            album = str((tags.get("\xa9alb") or tags.get("album") or [""])[0])
            genre = str((tags.get("\xa9gen") or tags.get("genre") or [""])[0])
    except Exception:
        pass
    if not title:
        title = os.path.splitext(os.path.basename(path))[0]
    return title, artist, album, genre


def analyze_file(file_path, models_dir):
    """Return a full track_analysis record dict for one audio file."""
    import essentia.standard as es

    title, artist, album, genre = _read_tags(file_path)
    rec = {"file_path": file_path, "title": title, "artist": artist,
           "album": album, "genre": genre,
           "genre_normalized": (genre or "").strip().lower(),
           "arousal": 0.0, "valence": 0.0}

    # BPM + energy at 44.1k
    try:
        audio_44k = es.MonoLoader(filename=file_path, sampleRate=44100)()
        rec["bpm"] = round(float(es.RhythmExtractor2013(method="multifeature")(audio_44k)[0]), 1)
        rec["energy"] = round(float(np.sqrt(np.mean(audio_44k ** 2))), 4)
    except Exception as e:
        log.warning("BPM/energy failed for %s: %s", file_path, e)
        rec.setdefault("bpm", 0.0)
        rec.setdefault("energy", 0.0)

    # Embeddings + mood/danceability heads at 16k
    try:
        audio_16k = es.MonoLoader(filename=file_path, sampleRate=16000, resampleQuality=4)()
        effnet = os.path.join(models_dir, "discogs-effnet-bs64-1.pb")
        embeddings = es.TensorflowPredictEffnetDiscogs(
            graphFilename=effnet, output="PartitionedCall:1")(audio_16k)
        for key, model_file in _MOOD_MODELS.items():
            mp = os.path.join(models_dir, model_file)
            rec[key] = (round(float(np.mean(es.TensorflowPredict2D(
                graphFilename=mp, output="model/Softmax")(embeddings)[:, 1])), 4)
                if os.path.exists(mp) else 0.0)
        dance = os.path.join(models_dir, "danceability-discogs-effnet-1.pb")
        rec["danceability"] = (round(float(np.mean(es.TensorflowPredict2D(
            graphFilename=dance, output="model/Softmax")(embeddings)[:, 1])), 4)
            if os.path.exists(dance) else 0.0)
    except Exception as e:
        log.error("embedding/mood inference failed for %s: %s", file_path, e)
        for k in _MOOD_KEYS:
            rec.setdefault(k, 0.0)

    return apply_context_boosts(rec, genre, rec.get("bpm", 0))
