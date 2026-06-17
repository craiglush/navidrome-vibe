# r/selfhosted

> **Read the rules first.** r/selfhosted restricts self-promotion (often a dedicated day/flair and
> a "you must be active in the community" expectation). Use the **"I made this"/release** flair if
> required, disclose you're the author in the first line, lead with the story, keep it to one link.
> Don't post the identical text you used elsewhere the same day.

**Title:** I built a self-hosted "describe a vibe → get a playlist" tool for Navidrome / Subsonic

**Body:**

Author here. I self-host my music on Navidrome and missed the streaming-service trick of "make me
a playlist for this moment", so I built an open-source companion for it.

You type a vibe — *"lazy Sunday morning with coffee"* — and it turns that into **human-readable
audio-feature ranges** (mood, energy, danceability, BPM), matches your library's
[essentia](https://essentia.upf.edu/) analysis, and creates a normal playlist that shows up in any
Subsonic client. The point of the ranges (vs. opaque embeddings) is you can see *why* a track was
chosen and tweak it.

Stack / how it self-hosts:
- Docker Compose: a small Flask app + an essentia analyzer; talks to your existing Navidrome (or
  any Subsonic server) over the API.
- **Local-first**: LLM defaults to your own Ollama; optional cheap hosted model if you've no GPU.
  essentia analysis runs on CPU.
- Optional Go/WASM Navidrome plugin for scheduled playlists.
- GPL-3.0.

It's early and solo (v0.1) — I've only proven the full loop on my own box (Navidrome 0.62, ~11k
tracks), so I'm sharing to get it in front of other setups. Known caveat: the analyzer has to scan
your library once before playlists work.

Repo + quick start: https://github.com/craiglush/navidrome-vibe

Happy to answer anything and would genuinely value "it broke on my setup" reports.
