"""Unit tests for entities: player movement/clamping, object typing,
spawning and the EffectTimer. Runs headless (see root conftest.py)."""
import pygame
import pytest

from src import settings
from src.entities import (
    Bomb,
    EffectTimer,
    FALLING_TYPES,
    GoldenApple,
    Item,
    MagnetPull,
    Player,
    SlowMotion,
    WidePaddle,
    spawn_falling_object,
)


class TestPlayerMovement:
    def test_starts_bottom_center(self):
        player = Player()
        assert player.rect.width == settings.PLAYER_WIDTH
        assert player.rect.centerx == settings.SCREEN_WIDTH // 2

    def test_moves_horizontally(self):
        player = Player()
        x0 = player.rect.x
        player.move(10)
        assert player.rect.x == x0 + 10

    def test_clamped_at_both_edges(self):
        player = Player()
        player.move(-10_000)
        assert player.rect.left == 0
        player.move(10_000)
        assert player.rect.right == settings.SCREEN_WIDTH

    def test_set_wide_grows_and_keeps_center(self):
        player = Player()
        center_x = player.rect.centerx
        player.set_wide(True)
        assert player.rect.width == round(
            settings.PLAYER_WIDTH * settings.WIDE_FACTOR
        )
        assert player.rect.centerx == center_x

    def test_set_wide_shrinks_back(self):
        player = Player()
        player.set_wide(True)
        player.set_wide(False)
        assert player.rect.width == settings.PLAYER_WIDTH

    def test_set_wide_near_edge_stays_on_screen(self):
        player = Player()
        player.move(-10_000)  # hug the left wall, then grow
        player.set_wide(True)
        assert player.rect.left == 0
        assert player.rect.right <= settings.SCREEN_WIDTH


class TestFallingObjectTypes:
    def test_item_attributes(self):
        assert (Item.points, Item.harmful, Item.penalize_on_miss) == (
            1,
            False,
            True,
        )

    def test_bomb_attributes(self):
        assert (Bomb.points, Bomb.harmful, Bomb.penalize_on_miss) == (
            0,
            True,
            False,
        )

    def test_golden_apple_double_points(self):
        assert GoldenApple.points == settings.GOLDEN_SCORE_MULTIPLIER == 2
        assert not GoldenApple.harmful and GoldenApple.penalize_on_miss

    @pytest.mark.parametrize(
        "cls", [WidePaddle, MagnetPull, SlowMotion], ids=lambda c: c.__name__
    )
    def test_powerup_config(self, cls):
        assert cls.effect_key and cls.effect_key in settings.POWERUP_LABELS
        assert cls.duration > 0
        assert not cls.harmful
        assert not cls.penalize_on_miss  # missing a power-up must be free

    def test_registry_covers_spawn_weights(self):
        assert set(FALLING_TYPES) == set(settings.SPAWN_WEIGHTS)


class TestFallingObjectMotion:
    def test_update_moves_at_base_speed(self):
        obj = Item()
        y0 = obj.rect.y
        obj.update()
        assert obj.rect.y == y0 + settings.ITEM_FALL_SPEED

    def test_update_speed_scale_is_slower_but_positive(self):
        obj = Item()
        y0 = obj.rect.y
        obj.update(settings.SLOWMO_SPEED_SCALE)
        step = obj.rect.y - y0  # Rect coords are ints, 3*0.4 truncates
        assert 0 < step < settings.ITEM_FALL_SPEED

    def test_off_screen_boundary(self):
        obj = Item()
        obj.rect.top = settings.SCREEN_HEIGHT
        assert not obj.off_screen()
        obj.rect.top = settings.SCREEN_HEIGHT + 1
        assert obj.off_screen()

    def test_spawner_returns_registered_types_above_screen(self):
        for _ in range(200):
            obj = spawn_falling_object()
            assert type(obj) in FALLING_TYPES.values()
            assert obj.rect.bottom <= 0  # always enters from the top


class TestEffectTimer:
    def test_activate_then_expire(self):
        timer = EffectTimer()
        assert not timer.active("wide")
        timer.activate("wide", 40)
        assert timer.active("wide") and timer.remaining("wide") > 0
        pygame.time.wait(100)
        assert not timer.active("wide")
        assert timer.remaining("wide") == 0.0

    def test_active_items_and_clear(self):
        timer = EffectTimer()
        timer.activate("magnet", 10_000)
        timer.activate("slowmo", 10_000)
        assert {key for key, _ in timer.active_items()} == {"magnet", "slowmo"}
        timer.clear()
        assert timer.active_items() == []
