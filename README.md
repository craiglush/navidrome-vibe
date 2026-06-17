# Vibe Playlists

**Describe a vibe, get a playlist — for Navidrome & any Subsonic server.**

Vibe Playlists is a self-hosted companion app for [Navidrome](https://www.navidrome.org/).
Type a scenario like *"rainy evening reading a book"* and it translates it into
human-readable audio-feature ranges (mood, energy, danceability, BPM …), matches them
against essentia analysis of your library, and creates a real playlist in your server —
visible in every Subsonic client.

Local-first: the LLM defaults to your own [Ollama](https://ollama.com). No GPU? Point it
at a cheap hosted model (Claude Haiku, or any OpenAI-compatible endpoint) instead.

> This repo is **Plan 1**: the companion app + vibe backend. The essentia **analyzer**
> service (which populates the analysis DB) and the **Navidrome plugin** (vibe-aware
> Instant Mix + scheduled packs) ship alongside it.

## Quick start

    git clone https://github.com/craiglush/navidrome-vibe
    cd navidrome-vibe
    cp .env.example .env        # edit NAVIDROME_* and your LLM provider
    docker compose up -d
    # open http://localhost:4546

You need a populated analysis DB at `ANALYSIS_DB_PATH` (the analyzer service produces it).

## Configuration

All config is via `.env` — see `.env.example`. Key settings: `NAVIDROME_URL/USER/PASSWORD`,
`VIBE_LLM_PROVIDER` (`ollama` default, or `openai` / `anthropic`), and the matching
provider block.

## Develop / test

    cd app && PYTHONPATH=. pytest -q

## License

GPL-3.0 — same as Navidrome.
