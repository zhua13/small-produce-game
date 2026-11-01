"""Local JSON persistence for the high-score table.

Scores live outside the repository, in the user's home directory
(``~/.small_produce/highscores.json`` by default), so a clone of the project
never carries save data. The path can be overridden (tests, portable saves).
"""
from __future__ import annotations

import json
import time
from pathlib import Path

DEFAULT_PATH = Path.home() / ".small_produce" / "highscores.json"
MAX_ENTRIES = 10
VERSION = 1


class HighScoreStore:
    """Top-N high scores backed by a small JSON file."""

    def __init__(self, path: "Path | str | None" = None) -> None:
        self.path = Path(path) if path is not None else DEFAULT_PATH
        self.scores: list[dict] = []
        self.load()

    def load(self) -> None:
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            self.scores = [
                {"score": int(entry["score"]), "date": str(entry["date"])}
                for entry in data.get("scores", [])
            ]
        except (OSError, ValueError, KeyError, TypeError):
            # Missing, unreadable or corrupt files simply start a fresh table.
            self.scores = []

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"version": VERSION, "scores": self.scores}
        self.path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def best(self) -> int:
        return self.scores[0]["score"] if self.scores else 0

    def submit(self, score: int) -> bool:
        """Try to record ``score``; returns True when it made the top list."""
        if score <= 0:
            return False
        entry = {"score": int(score), "date": time.strftime("%Y-%m-%d %H:%M")}
        candidates = sorted(
            self.scores + [entry], key=lambda e: e["score"], reverse=True
        )[:MAX_ENTRIES]
        recorded = entry in candidates
        if recorded:
            self.scores = candidates
            self.save()
        return recorded
