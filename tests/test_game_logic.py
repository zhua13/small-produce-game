"""Headless tests for the Game loop: collision resolution, scoring,
life penalties, power-up activation and the game-over flow."""
import pygame
import pytest

from src import settings
from src.entities import Bomb, Item, WidePaddle
from src.game import Game
from src.storage import HighScoreStore


@pytest.fixture()
def game(tmp_path):
    """A Game writing high scores into the test's tmp directory."""
    instance = Game(highscore_path=tmp_path / "highscores.json")
    instance.reset()
    yield instance
    pygame.quit()


def place_on_player(game: Game, obj):
    """Position a falling object so it overlaps the paddle next update."""
    obj.rect.midbottom = (
        game.player.rect.midtop[0],
        game.player.rect.midtop[1] + 5,
    )
    game.falling = [obj]


def place_off_screen(obj):
    obj.rect.top = settings.SCREEN_HEIGHT + 1
    return obj


class TestCollisions:
    def test_catching_item_scores(self, game):
        item = Item()
        place_on_player(game, item)
        game.update()
        assert game.score == Item.points
        assert item not in game.falling
        assert game.lives == settings.START_LIVES

    def test_catching_bomb_costs_a_life(self, game):
        place_on_player(game, Bomb())
        game.update()
        assert game.lives == settings.START_LIVES - 1
        assert game.score == 0

    def test_missed_item_costs_a_life(self, game):
        item = Item()
        place_off_screen(item)
        game.falling = [item]
        game.update()
        assert game.lives == settings.START_LIVES - 1

    def test_missed_powerup_is_free(self, game):
        game.falling = [place_off_screen(WidePaddle())]
        lives_before = game.lives
        game.update()
        assert game.lives == lives_before
        assert not game.effects.active("wide")


class TestPowerups:
    def test_catching_powerup_activates_effect_then_widens_paddle(self, game):
        place_on_player(game, WidePaddle())
        game.update()
        assert game.effects.active("wide")
        game.update()
        assert game.player.rect.width == round(
            settings.PLAYER_WIDTH * settings.WIDE_FACTOR
        )


class TestGameOver:
    def test_final_score_is_persisted(self, game, tmp_path):
        game.score = 42
        game.lives = 1
        place_on_player(game, Bomb())
        game.update()
        assert game.game_over and game.lives == 0
        assert game.new_record
        assert HighScoreStore(tmp_path / "highscores.json").best() == 42

    def test_zero_score_game_over_is_not_recorded(self, game, tmp_path):
        game.lives = 1
        place_on_player(game, Bomb())
        game.update()
        assert game.game_over
        assert not (tmp_path / "highscores.json").exists()

    def test_restart_after_game_over(self, game):
        game.score = 10
        game.lives = 0
        game.game_over = True
        pygame.event.post(
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_r)
        )
        assert game.handle_events()
        assert not game.game_over
        assert game.score == 0
        assert game.lives == settings.START_LIVES
