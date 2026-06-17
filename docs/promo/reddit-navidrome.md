# r/navidrome (and the Navidrome forum / Discord)

**Title:** I built a "describe a vibe → get a playlist" companion for Navidrome (open source)

**Body:**

I made [navidrome-mood-plugin](https://github.com/craiglush/navidrome-mood-plugin) a while back; this
is the thing I actually wanted next — typing a mood and getting a playlist.

You type something like *"rainy evening reading a book"* and it turns that into human-readable
audio-feature ranges (e.g. `relaxed ≥ 0.5, energy < 0.15, bpm < 100`), matches your library's
essentia analysis, and creates a normal playlist via the Subsonic API — so it appears in the
Navidrome web UI and any Subsonic client.

It's three small pieces that sit alongside your existing Navidrome:
- a **companion web app** with the interactive "type a vibe" box,
- an **essentia analyzer** that scans your library once, and
- an optional **Navidrome plugin** (needs 0.60+ with plugins enabled) for scheduled "Vibe of the
  Day" playlists + an "Instant Vibe" field. (I left Instant Mix to the mood plugin.)

Local-first: LLM defaults to your own Ollama; a cheap hosted model works too if you've no GPU.

Honest disclaimer: I'm the author, it's early/solo (v0.1), and I've only proven it on my own setup
(Navidrome 0.62, ~11k tracks). Posting because I'd love feedback from people running different
libraries/clients.

Repo + quick start: https://github.com/craiglush/navidrome-vibe (GPL-3.0)

What I'd most like to know: does the quick start work on your setup, and do the feature ranges
match what you'd expect for a given vibe?

> Posting notes: r/navidrome is small and friendly — this is fine as-is. Also drop the short
> Discord blurb (see discord-lemmy.md) in the Navidrome Discord #showcase/#plugins channel.
