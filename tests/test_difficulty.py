"""Tests for the difficulty curve: level progression from score, spawn
chance scaling, fall speed steps and the growing bomb share."""
import random

import pygame
import pytest

from src import settings
from src.entities import Bomb, spawn_falling_object
from src.game import Game


@pytest.fixture()
def game(tmp_path):
    instance = Game(highscore_path=tmp_path / "highscores.json")
    instance.reset()
    yield instance
    pygame.quit()


class TestSpawnChance:
    def test_grows_monotonically(self):
        chances = [
            settings.spawn_chance_for_level(lv)
            for lv in range(settings.MAX_LEVEL + 2)
        ]
        assert all(a < b for a, b in zip(chances, chances[1:]))

    def test_negative_level_falls_back_to_base(self):
        assert settings.spawn_chance_for_level(-3) == settings.SPAWN_CHANCE


class TestLevelSpeedAndBombs:
    def test_base_speed_at_level_zero(self):
        assert spawn_falling_object(level=0).speed == settings.ITEM_FALL_SPEED

    def test_speed_steps_up_with_level(self):
        obj = spawn_falling_object(level=4)
        assert obj.speed == (
            settings.ITEM_FALL_SPEED + 4 * settings.FALL_SPEED_PER_LEVEL
        )

    def test_negative_level_is_clamped(self):
        assert spawn_falling_object(level=-5).speed == settings.ITEM_FALL_SPEED

    def test_bomb_share_grows_with_level(self):
        random.seed(3)
        samples = 6000

        def bomb_share(level: int) -> float:
            return sum(
                isinstance(spawn_falling_object(level), Bomb)
                for _ in range(samples)
            ) / samples

        low, high = bomb_share(0), bomb_share(8)
        assert high > low + 0.05  # ~25% -> ~41% expected


class TestGameLevel:
    def test_level_derives_from_score_and_caps(self, game):
        game.score = 0
        assert game.level == 0
        game.score = 25
        assert game.level == 2
        game.score = settings.POINTS_PER_LEVEL * settings.MAX_LEVEL + 99
        assert game.level == settings.MAX_LEVEL

    def test_update_spawn_chance_follows_level(self, game, monkeypatch):
        # A roll just above the base chance: spawns only once levelled up.
        roll = settings.spawn_chance_for_level(0) + 1e-9
        monkeypatch.setattr(random, "random", lambda: roll)

        game.score = 0
        game.update()
        assert game.falling == []

        game.score = settings.POINTS_PER_LEVEL  # level 1 raises the chance
        game.update()
        assert len(game.falling) >= 1

    def test_spawned_objects_inherit_current_speed(self, game, monkeypatch):
        monkeypatch.setattr(random, "random", lambda: 0.0)  # force a spawn
        game.score = settings.POINTS_PER_LEVEL * 3  # level 3
        game.update()
        assert game.falling
        expected = settings.ITEM_FALL_SPEED + 3 * settings.FALL_SPEED_PER_LEVEL
        assert all(obj.speed >= expected for obj in game.falling)
