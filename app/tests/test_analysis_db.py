def test_init_and_all_tracks(analysis_db):
    rows = analysis_db.all_tracks()
    assert len(rows) == 3
    assert {r["title"] for r in rows} == {"Calm One", "Party Two", "Sad Three"}


def test_count(analysis_db):
    assert analysis_db.count() == 3


def test_empty_db_count(tmp_path):
    from vibe.analysis_db import AnalysisDB
    db = AnalysisDB(str(tmp_path / "empty.db"))
    db.init_schema()
    assert db.count() == 0
    assert db.all_tracks() == []
