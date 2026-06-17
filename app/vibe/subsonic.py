"""Subsonic-API client (works with Navidrome and any Subsonic-compatible server).

Auth uses the standard MD5 salt+token scheme. get_all_songs/get_starred use
Navidrome's native paginated API when available (Subsonic getStarred2 caps
results); they degrade gracefully if that endpoint is absent.
"""

import hashlib
import logging
import random
import string

import requests

log = logging.getLogger(__name__)
CLIENT_NAME = "navidrome-vibe"
API_VERSION = "1.16.1"


class SubsonicClient:
    def __init__(self, url: str, user: str, password: str):
        self.url = url.rstrip("/")
        self.user = user
        self.password = password
        self._jwt = None

    def _auth_params(self):
        salt = "".join(random.choices(string.ascii_lowercase + string.digits, k=12))
        token = hashlib.md5((self.password + salt).encode()).hexdigest()
        return {"u": self.user, "t": token, "s": salt,
                "v": API_VERSION, "c": CLIENT_NAME, "f": "json"}

    def _get(self, endpoint, **params):
        resp = requests.get(f"{self.url}/rest/{endpoint}",  # safe: f-string URL, not SQL
                            params={**self._auth_params(), **params}, timeout=30)
        resp.raise_for_status()
        inner = resp.json().get("subsonic-response", {})
        if inner.get("status") != "ok":
            msg = inner.get("error", {}).get("message", "unknown")
            raise RuntimeError(f"Subsonic API error: {msg}")
        return inner

    # ── JWT (Navidrome native API) ──────────────────────────────
    def _jwt_token(self):
        if self._jwt is None:
            resp = requests.post(f"{self.url}/auth/login",  # safe: f-string URL, not SQL
                                 json={"username": self.user, "password": self.password},
                                 timeout=10)
            resp.raise_for_status()
            self._jwt = resp.json()["token"]
        return self._jwt

    def _native_get(self, path, **params):
        token = self._jwt_token()
        headers = {"Authorization": f"Bearer {token}",
                   "x-nd-authorization": f"Bearer {token}"}
        resp = requests.get(f"{self.url}{path}", params=params, headers=headers, timeout=60)  # safe: f-string URL, not SQL
        resp.raise_for_status()
        return resp

    # ── Playlists ───────────────────────────────────────────────
    def get_playlists(self):
        return self._get("getPlaylists").get("playlists", {}).get("playlist", [])

    def delete_playlist(self, playlist_id):
        self._get("deletePlaylist", id=playlist_id)

    def create_playlist(self, name, song_ids):
        param_str = "&".join(
            [f"{k}={requests.utils.quote(str(v))}"
             for k, v in {**self._auth_params(), "name": name}.items()]
            + [f"songId={requests.utils.quote(str(s))}" for s in song_ids]
        )
        resp = requests.get(f"{self.url}/rest/createPlaylist?{param_str}", timeout=30)  # safe: f-string URL, not SQL
        resp.raise_for_status()
        inner = resp.json().get("subsonic-response", {})
        if inner.get("status") != "ok":
            msg = inner.get("error", {}).get("message", "unknown")
            raise RuntimeError(f"Playlist creation failed: {msg}")
        return inner.get("playlist", {}).get("id")

    # ── Songs / search / starred ────────────────────────────────
    def search(self, query, song_count=5):
        resp = self._get("search3", query=query, songCount=song_count,
                         albumCount=0, artistCount=0)
        return resp.get("searchResult3", {}).get("song", [])

    def get_all_songs(self, page_size=500):
        """All songs via Navidrome native paginated API."""
        out, start, total = [], 0, None
        while True:
            try:
                resp = self._native_get("/api/song", _start=start,
                                        _end=start + page_size, _sort="title", _order="ASC")
                if total is None:
                    total = int(resp.headers.get("X-Total-Count", 0))
                batch = resp.json()
                if not batch:
                    break
                out.extend(batch)
                start += len(batch)
                if total and start >= total:
                    break
            except Exception as e:
                log.warning("get_all_songs stopped at %d: %s", start, e)
                break
        return out

    def get_starred(self, page_size=500):
        """All starred songs via native paginated API."""
        out, start, total = [], 0, None
        while True:
            try:
                resp = self._native_get("/api/song", _start=start,
                                        _end=start + page_size, _sort="title",
                                        _order="ASC", starred=True)
                if total is None:
                    total = int(resp.headers.get("X-Total-Count", 0))
                batch = resp.json()
                if not batch:
                    break
                out.extend(batch)
                start += len(batch)
                if total and start >= total:
                    break
            except Exception as e:
                log.warning("get_starred stopped at %d: %s", start, e)
                break
        return out
