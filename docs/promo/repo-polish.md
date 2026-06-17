# GitHub repo polish

Do this **before** posting anywhere — visitors should land on something finished.

## About / description (≤ 350 chars)
> Describe a vibe, get a playlist — for Navidrome & any Subsonic server. A self-hosted companion
> that turns free text into human-readable audio-feature ranges over essentia analysis and builds
> playlists from your own library. Local-first (Ollama), optional plugin. GPL-3.0.

Website field: leave blank, or point at the dev.to article once published.

## Topics (Settings → Topics)
```
navidrome  navidrome-plugin  subsonic  self-hosted  music  playlists  ollama  essentia  llm  docker
```
(`navidrome-plugin` matters — it's the de-facto discovery tag and where your mood plugin already shows up.)

## Social preview (Settings → Social preview)
Upload a 1280×640 image — simplest is a clean screenshot of the "type a vibe" box with one example
prompt + the resulting playlist. One-line overlay:
> **Vibe Playlists** — describe a mood, get a playlist. Self-hosted, for Navidrome.

## Demo GIF storyboard (the key asset — record this first)
Target 5–10s, looped, ≤ ~5 MB. Tools: ScreenToGif / LICEcap / `ffmpeg`.

1. **(0–1s)** Companion app open on the "Describe a vibe" box, empty. Caption: *"Type a vibe."*
2. **(1–3s)** Type `rainy evening reading a book` into the box (real keystrokes).
3. **(3–4s)** Click **Create playlist**; show the "thinking…" state briefly.
4. **(4–6s)** Result card appears: playlist name + the chosen ranges (`relaxed ≥ 0.5, energy < 0.15…`) + a few track rows. Caption: *"See why each track matched."*
5. **(6–8s)** Cut to Navidrome showing the new playlist in the sidebar / playing the first track. Caption: *"It's a real playlist — in every Subsonic client."*
6. **(8–10s)** Hold on the playlist for the loop.

Keep captions short and burned-in (many viewers autoplay muted). A second, shorter GIF of the
plugin's **Instant Vibe** field (type + Save → playlist appears) is a nice bonus for the plugin
section.

## README touch-ups
- Put the GIF right under the title.
- Add a one-line comparison note (fair, not dismissive) so people arriving from "AI playlist
  Navidrome" understand the niche: *"Unlike embedding-based tools, the matching is transparent —
  you see and can tune the feature ranges behind each vibe."* (Already in the README intro/How-it-works.)
- A "Status: early/solo" line so expectations are set.
