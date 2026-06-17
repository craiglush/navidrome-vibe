# Vibe Playlists

**Describe a vibe, get a playlist — for [Navidrome](https://www.navidrome.org/) & any Subsonic server.**

Type a scenario like *"rainy evening reading a book"* or *"Friday night pre-drinks"* and Vibe
Playlists turns it into a real playlist in your music server. An LLM translates your words into
**human-readable audio-feature ranges** (mood, energy, danceability, BPM, arousal, valence …),
matches them against an essentia analysis of your library, and creates a playlist that shows up
in every Subsonic client (the Navidrome web UI, Symfonium, Feishin, play:Sub, …).

**Local-first.** The LLM defaults to your own [Ollama](https://ollama.com). No GPU? Point it at
a cheap hosted model (Claude Haiku, or any OpenAI-compatible endpoint) — one line of config.

> **Status:** the companion app and the **essentia analyzer** are functional. Bring up both
> with `docker compose up -d`, point the analyzer at your music library (`MUSIC_DIR`), and it
> populates the analysis DB. A **Navidrome plugin** (vibe-aware Instant Mix + scheduled packs)
> is still on the [roadmap](#roadmap).

## How it works

```
You type a vibe ──▶ /api/vibe ──▶ LLM (Ollama by default)
                                     │  "rainy evening" → feature ranges
                                     ▼
                       query track_analysis (essentia) ──▶ score & rank tracks
                                     │
                                     ▼
                    match to your library ──▶ createPlaylist (Subsonic API)
                                     │
                                     ▼
                    playlist appears in every Subsonic client
```

Unlike embedding-based tools, the matching is **transparent**: each vibe maps to explicit,
inspectable feature ranges (e.g. `relaxed ≥ 0.5, energy < 0.15, bpm < 100`), so you can see
*why* a track was chosen — and tune it.

## Features

- **Free-text → playlist** — describe any scenario; the LLM picks the audio-feature ranges.
- **Pluggable LLM, local-first** — Ollama by default; OpenAI-compatible and Anthropic optional.
- **Works with any Subsonic server** — playlists are created via the standard Subsonic API.
- **Favourite-aware** — starred tracks get a relevance boost.
- **Genre exclusions** — keep genres you don't want out of a vibe.
- **No GPU required** — analysis runs on CPU; a hosted LLM removes the local-model requirement.

## Quick start

```bash
git clone https://github.com/craiglush/navidrome-vibe
cd navidrome-vibe
cp .env.example .env        # set NAVIDROME_* and your LLM provider
docker compose up -d
# open http://localhost:4546   (set VIBE_PORT in .env to change the port)
```

## Requirements

- A running **Navidrome** (or any Subsonic-compatible server) and an account on it.
- The bundled **analyzer** service (set `MUSIC_DIR` to your library) populates the analysis DB
  on first run; or bring your own `track_analysis` SQLite DB.
- An **LLM endpoint**: a local Ollama (default) *or* a hosted OpenAI-compatible / Anthropic key.

## Configuration

All configuration is via environment variables — see [`.env.example`](.env.example).

| Variable | Default | Purpose |
|----------|---------|---------|
| `NAVIDROME_URL` | `http://navidrome:4533` | Your Subsonic/Navidrome server |
| `NAVIDROME_USER` / `NAVIDROME_PASSWORD` | `admin` / – | Account playlists are created under |
| `VIBE_LLM_PROVIDER` | `ollama` | `ollama` \| `openai` \| `anthropic` |
| `OLLAMA_URL` / `OLLAMA_MODEL` | `http://host.docker.internal:11434` / `qwen2.5:7b` | Local Ollama |
| `OPENAI_BASE_URL` / `OPENAI_API_KEY` / `OPENAI_MODEL` | – | Any OpenAI-compatible endpoint (Open WebUI, LM Studio, OpenAI…) |
| `ANTHROPIC_API_KEY` / `ANTHROPIC_MODEL` | – / `claude-haiku-4-5` | Hosted Claude (cheap, no GPU) |
| `ANALYSIS_DB_PATH` / `VIBE_DB_PATH` | `/data/analysis.db` / `/data/vibe.db` | SQLite paths |
| `VIBE_API_TOKEN` | – | If set, `/api/vibe` requires `Authorization: Bearer <token>` |
| `VIBE_PORT` | `4546` | Web UI / API port |

## Analyzer

The `analyzer` service scans `MUSIC_DIR` with essentia-tensorflow and writes per-track mood,
BPM, energy and danceability into the shared analysis DB. It scans on startup
(`SCAN_ON_START=true`) and can be re-triggered:

    curl -X POST http://localhost:8000/api/scan
    # or one-shot:
    docker compose run --rm analyzer python -m analyzer scan

Analysis runs on CPU (no GPU required). The first full scan of a large library takes a while;
subsequent scans skip already-analyzed files.

## API

```http
POST /api/vibe
Content-Type: application/json

{ "prompt": "lazy Sunday morning with coffee", "count": 30 }
```

Returns the created playlist (id, name, the LLM's reasoning, the chosen feature ranges, and a
track preview). Other routes: `GET /healthz`, `GET /api/vibe/history`,
`DELETE /api/vibe/history/<id>`.

## Develop / test

```bash
cd app
python -m venv .venv && .venv/bin/pip install -r requirements.txt   # Windows: .venv/Scripts/pip
PYTHONPATH=. .venv/bin/pytest -q
```

## Roadmap

- [x] Bundled **essentia analyzer** service (populates `track_analysis` from your library)
- [ ] **Navidrome plugin** — vibe-aware Instant Mix + scheduled "Vibe of the Day" packs
- [ ] Optional multi-user / public-playlist sharing
- [ ] Save & re-run favourite vibes

## License

[GPL-3.0](LICENSE) — same as Navidrome.
