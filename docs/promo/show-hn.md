# Show HN

> Post only when the README + demo GIF are solid and you can be around for a few hours to reply.
> HN "Show HN" rules: it must be something people can try; title starts with "Show HN:"; keep it
> plain. Put the detail in your own first comment.

## Title (<80 chars)
`Show HN: Describe a vibe, get a playlist – self-hosted, for Navidrome/Subsonic`

## URL
`https://github.com/craiglush/navidrome-vibe`

## Your first comment (post immediately after submitting)
I self-host my music with Navidrome and missed the "make me a playlist for this moment" thing from
streaming, so I built it for my own library.

You type a vibe ("rainy evening reading a book") and a local LLM converts it into human-readable
audio-feature ranges — e.g. `relaxed ≥ 0.5, energy < 0.15, bpm < 100` — which are matched against
essentia analysis of your library to build a normal playlist (written back via the Subsonic API,
so it appears in every client). The deliberate design choice vs. embedding-based approaches is
**legibility**: you can see and tune why a track was chosen.

It's local-first (defaults to your own Ollama; a cheap hosted model works if you've no GPU; the
essentia analysis runs on CPU), Docker Compose, GPL-3.0. There's also an optional Go/WASM Navidrome
plugin for scheduled playlists.

Caveats, since it's early and solo (v0.1): the analyzer has to scan your library once before
anything works, and I've only verified the full loop on my own setup (Navidrome 0.62, ~11k tracks).
Keen for feedback, especially on whether the feature ranges match what you'd expect for a vibe.
