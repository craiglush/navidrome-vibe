# Vibe Playlists

**Describe a vibe, get a playlist — for [Navidrome](https://www.navidrome.org/) & any Subsonic server.**

![License: GPL-3.0](https://img.shields.io/badge/license-GPL--3.0-blue) &nbsp;![Navidrome 0.60+](https://img.shields.io/badge/Navidrome-0.60%2B-blue) &nbsp;![Subsonic compatible](https://img.shields.io/badge/Subsonic-compatible-success) &nbsp;![Local-first](https://img.shields.io/badge/LLM-local--first%20(Ollama)-d4a039)

*Demo GIF coming — shot list in [`docs/promo/repo-polish.md`](docs/promo/repo-polish.md).*

Type a scenario like *"rainy evening reading a book"* or *"Friday night pre-drinks"* and Vibe
Playlists turns it into a real playlist in your music server. An LLM translates your words into
**human-readable audio-feature ranges** (mood, energy, danceability, BPM, and genre context),
matches them against an essentia analysis of your library, and creates a playlist that shows up
in every Subsonic client (the Navidrome web UI, Symfonium, Feishin, play:Sub, …).

**Local-first.** The LLM defaults to your own [Ollama](https://ollama.com). No GPU? Point it at
a cheap hosted model (Claude Haiku, or any OpenAI-compatible endpoint) — one line of config.

> **Status:** early but working (v0.1). All three parts — the companion app, the **essentia
> analyzer**, and the **Navidrome plugin** — are built and verified end-to-end against a live
> Navidrome 0.62 with an ~11k-track library. It's solo and not yet battle-tested on other setups,
> so issues and feedback are very welcome. The analyzer must scan your library once before
> playlists work.

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

The `analyzer` service scans `MUSIC_DIR` with essentia-tensorflow and writes per-track features
into the shared analysis DB. It extracts **BPM, energy, danceability, and 5 moods** (happy, sad,
relaxed, aggressive, party), with genre/BPM context boosts. (Arousal and valence are deferred —
stored as 0.0 for schema compatibility.)

It scans on startup (`SCAN_ON_START=true`); to re-trigger:

    # one-shot scan (recommended):
    docker compose run --rm analyzer python -m analyzer scan

The analyzer's HTTP API (port 8000) is internal to the compose network and not published by
default. During an active scan, the app's read queries may briefly wait (SQLite WAL, 30s timeout)
— this is normal. Analysis runs on CPU (no GPU required); the first full scan of a large library
takes a while, and subsequent scans skip already-analyzed files.

## Navidrome plugin (optional)

A thin Navidrome plugin generates **"Vibe of the Day"** playlists on a schedule by calling this
app's `/api/vibe` for each prompt you configure. It surfaces vibe playlists natively in
Navidrome with no interaction required.

Requires Navidrome 0.60+ with plugins enabled (`ND_PLUGINS_ENABLED=true`).

1. Build it: `cd plugin && make docker-build` (produces `vibe-playlists.ndp`), or download from Releases.
2. Copy `vibe-playlists.ndp` into your Navidrome `plugins/` directory and restart Navidrome.
3. In **Settings → Plugins → Vibe Playlists**, approve permissions, then set the
   **Companion App URL**, your **vibe prompts** (one per line), and the **refresh schedule**.
   - Use `http://vibe:4546` only if the plugin's Navidrome and this app share a Docker network.
     If the app runs as a **separate stack** (the common case), use `http://host.docker.internal:4546`
     (Docker Desktop) or your host's LAN address.

> **Heads-up:** updating the `.ndp` (any rebuild) makes Navidrome **disable the plugin and reset its
> config to defaults**. After every plugin update, re-enable it and re-check the Companion App URL,
> prompts, and schedule.

**Instant Vibe:** to generate a single playlist on demand from inside Navidrome, type a prompt into
the plugin's **Instant Vibe** settings field and click **Save** — saving re-runs the plugin and
generates that one playlist (it won't repeat on restart unless you change the text). The richer
"type any vibe" box with live results is in the companion app's web UI.

The interactive "type any vibe" experience lives in the companion app's web UI; the plugin is for
scheduled, hands-off playlists. Generation runs **asynchronously** (the app returns immediately and
builds the playlist in the background), so it stays within Navidrome's scheduler-callback deadline.
(Instant Mix is provided by the separate
[navidrome-mood-plugin](https://github.com/craiglush/navidrome-mood-plugin).)

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
- [x] **Navidrome plugin** — scheduled "Vibe of the Day" packs
- [ ] Optional multi-user / public-playlist sharing
- [ ] Save & re-run favourite vibes

## License

[GPL-3.0](LICENSE) — same as Navidrome.
