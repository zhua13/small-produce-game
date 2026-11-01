"""Asset pipeline tests: generated files exist, loading populates the cache
and rendering falls back to flat colors when sprites are unavailable."""
import pygame
import pytest

from src import assets
from src.entities import FALLING_TYPES, Item, Player
from src.game import Game

EXPECTED_SPRITES = [*FALLING_TYPES, "player"]
EXPECTED_SOUNDS = ["catch", "bomb", "gameover"]


def test_generated_files_exist():
    for name in EXPECTED_SPRITES:
        assert (assets.SPRITE_DIR / f"{name}.png").exists(), name
    for name in EXPECTED_SOUNDS:
        assert (assets.SOUND_DIR / f"{name}.wav").exists(), name


@pytest.fixture()
def game(tmp_path):
    instance = Game(highscore_path=tmp_path / "hs.json")
    yield instance
    pygame.quit()


def test_sprites_and_sounds_loaded(game):
    for name in EXPECTED_SPRITES:
        assert assets.image(name) is not None, name
    if pygame.mixer.get_init():  # silent dummy driver still initializes
        for name in EXPECTED_SOUNDS:
            assert assets.sound(name) is not None, name


def test_scaled_image_size_and_cache(game):
    img = assets.scaled_image("item", (22, 22))
    assert img.get_size() == (22, 22)
    assert assets.scaled_image("item", (22, 22)) is img  # cached instance


def test_draw_frame_with_sprites(game):
    item = Item()
    item.rect.center = (240, 300)
    game.falling = [item]
    game.draw()  # sprite blit path must not raise


def test_flat_color_fallback_without_assets(game, monkeypatch):
    monkeypatch.setattr(assets, "_images", {})
    player = Player()
    player.set_wide(True)
    game.falling = [Item()]
    game.draw()  # entities must fall back to plain rectangles
