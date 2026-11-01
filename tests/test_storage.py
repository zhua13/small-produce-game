"""Unit tests for the JSON high-score store, using pytest's tmp_path so
the real user home directory is never touched."""
import json

from src.storage import MAX_ENTRIES, VERSION, HighScoreStore


def store_at(tmp_path):
    return HighScoreStore(tmp_path / "highscores.json")


def test_fresh_store_is_empty(tmp_path):
    store = store_at(tmp_path)
    assert store.scores == []
    assert store.best() == 0


def test_submit_sorts_and_persists(tmp_path):
    store = store_at(tmp_path)
    for score in (5, 12, 9):
        assert store.submit(score)
    assert [entry["score"] for entry in store.scores] == [12, 9, 5]
    assert store.best() == 12

    data = json.loads(store.path.read_text(encoding="utf-8"))
    assert data["version"] == VERSION
    assert len(data["scores"]) == 3


def test_zero_and_negative_scores_ignored(tmp_path):
    store = store_at(tmp_path)
    assert not store.submit(0)
    assert not store.submit(-3)
    assert not store.path.exists()


def test_table_capped_at_max_entries(tmp_path):
    store = store_at(tmp_path)
    for score in range(1, 13):  # 12 submissions, top 10 kept
        store.submit(score)
    assert len(store.scores) == MAX_ENTRIES
    assert store.scores[0]["score"] == 12
    assert store.scores[-1]["score"] == 3


def test_low_score_not_recorded_when_full(tmp_path):
    store = store_at(tmp_path)
    for score in range(101, 111):
        assert store.submit(score)
    assert not store.submit(50)
    assert store.best() == 110
    assert len(store.scores) == MAX_ENTRIES


def test_roundtrip_between_instances(tmp_path):
    path = tmp_path / "highscores.json"
    HighScoreStore(path).submit(7)
    assert HighScoreStore(path).best() == 7


def test_corrupt_file_starts_fresh_table(tmp_path):
    store = store_at(tmp_path)
    store.path.write_text("{{{not json", encoding="utf-8")
    store.load()
    assert store.scores == []
    assert store.submit(1)  # still usable afterwards
