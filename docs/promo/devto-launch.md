---
title: "Vibe Playlists: describe a mood, get a playlist — for self-hosted Navidrome"
tags: selfhosted, navidrome, opensource, music
canonical_url: https://github.com/craiglush/navidrome-vibe
---

> Draft for dev.to. Replace the GIF placeholder before publishing. Suggested tags: `selfhosted`, `navidrome`, `opensource`, `music` (dev.to allows up to 4).

I self-host my music on [Navidrome](https://www.navidrome.org/). The one thing I missed from the
streaming services was the "make me a playlist for *this moment*" feeling — so I built it, for my
own library, and put it on GitHub: **[Vibe Playlists](https://github.com/craiglush/navidrome-vibe)** (GPL-3.0).

You type a vibe — *"rainy evening reading a book"*, *"lazy Sunday morning with coffee"* — and it
creates a real playlist in your server that shows up in every Subsonic client (the Navidrome web
UI, Symfonium, Feishin, …).

![type a vibe → a playlist appears](REPLACE-WITH-DEMO.gif)
<!-- GIF: type a vibe in the box → the playlist appears in Navidrome. See docs/promo/repo-polish.md for the shot list. -->

## What makes it different

There's already a great tool in this space — [AudioMuse-AI](https://github.com/NeptuneHub/AudioMuse-AI) — so I want to be clear about *why this exists*.

Vibe Playlists is **transparent**. Your words are turned into **human-readable audio-feature
ranges**, and you can see exactly why a track was picked:

```
"rainy evening reading a book"
→ mood_relaxed ≥ 0.5,  energy < 0.15,  bpm < 100,  danceability < 0.2
```

No black-box embeddings — just ranges over [essentia](https://essentia.upf.edu/) analysis
(mood, energy, danceability, BPM) that you can read and tune.

## How it works

```
type a vibe ──▶ LLM turns it into feature ranges ──▶ match your library's essentia analysis
            ──▶ create a normal playlist via the Subsonic API ──▶ shows up in every client
```

Three small pieces:

1. **Companion app** — a web box where you type a vibe and get an instant playlist (plus a JSON API).
2. **Analyzer** — an essentia service that scans your library once and stores per-track features.
3. **Navidrome plugin** *(optional)* — scheduled "Vibe of the Day" playlists, and an "Instant Vibe" field, all from inside Navidrome.

## Local-first, no GPU required

The LLM defaults to your own [Ollama](https://ollama.com). No GPU? Point it at a cheap hosted
model (Claude Haiku, or any OpenAI-compatible endpoint) — one line of config. The essentia
analysis runs on CPU.

## Quick start

```bash
git clone https://github.com/craiglush/navidrome-vibe
cd navidrome-vibe
cp .env.example .env        # set your Navidrome details + LLM provider
docker compose up -d        # app + analyzer; point the analyzer at your library
# open http://localhost:4546
```

The analyzer populates the feature DB on first run; then type away.

## Honest status

It's **early and solo** (v0.1). I've run the whole loop against my own ~11k-track library on
Navidrome 0.62, but it hasn't been battle-tested by anyone else yet — which is exactly why I'm
posting. Issues, ideas, and "this broke on my setup" reports are all very welcome.

Repo: **https://github.com/craiglush/navidrome-vibe** · GPL-3.0 (same as Navidrome).
