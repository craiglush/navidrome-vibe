import responses
from vibe.subsonic import SubsonicClient


def _client():
    return SubsonicClient("http://nd.test", "tester", "pw")


@responses.activate
def test_create_playlist_returns_id():
    responses.add(
        responses.GET, "http://nd.test/rest/createPlaylist",
        json={"subsonic-response": {"status": "ok", "playlist": {"id": "pl-99"}}},
        status=200,
    )
    pid = _client().create_playlist("My Vibe", ["s1", "s2"])
    assert pid == "pl-99"
    qs = responses.calls[0].request.url
    assert "songId=s1" in qs and "songId=s2" in qs
    assert "name=My+Vibe" in qs or "name=My%20Vibe" in qs


@responses.activate
def test_api_error_raises():
    responses.add(
        responses.GET, "http://nd.test/rest/getPlaylists",
        json={"subsonic-response": {"status": "failed",
                                    "error": {"message": "nope"}}},
        status=200,
    )
    try:
        _client().get_playlists()
        assert False, "expected RuntimeError"
    except RuntimeError as e:
        assert "nope" in str(e)


@responses.activate
def test_get_playlists_returns_list():
    responses.add(
        responses.GET, "http://nd.test/rest/getPlaylists",
        json={"subsonic-response": {"status": "ok",
              "playlists": {"playlist": [{"id": "p1", "name": "A"}]}}},
        status=200,
    )
    assert _client().get_playlists() == [{"id": "p1", "name": "A"}]


@responses.activate
def test_search_returns_songs():
    responses.add(
        responses.GET, "http://nd.test/rest/search3",
        json={"subsonic-response": {"status": "ok",
              "searchResult3": {"song": [{"id": "s1", "title": "T"}]}}},
        status=200,
    )
    assert _client().search("T")[0]["id"] == "s1"
