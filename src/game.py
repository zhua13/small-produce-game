"""Main game loop, input handling, collision detection and rendering.

Run through ``main.py``. The ``Game`` class owns the pygame surface, the frame
clock and the whole play field, so additional gameplay features can be added
here without touching the entity definitions.
"""
import random

import pygame

from . import assets, settings
from .entities import (
    EffectTimer,
    FallingObject,
    Player,
    PowerUp,
    spawn_falling_object,
)
from .storage import HighScoreStore


class Game:
    def __init__(self, highscore_path=None) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode(
            (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
        )
        pygame.display.set_caption(settings.CAPTION)
        self.clock = pygame.time.Clock()
        # Font(None) uses pygame's bundled default font, which avoids the
        # Windows system-font registry scan (and its quirks) entirely.
        self.font = pygame.font.Font(None, 32)
        # Mixer may be unavailable (no audio device); assets.load() then
        # skips sounds and playback helpers stay silent.
        if not pygame.mixer.get_init():
            try:
                pygame.mixer.init()
            except pygame.error:
                pass
        assets.load()
        self.highscores = HighScoreStore(highscore_path)
        self.reset()

    def reset(self) -> None:
        """Reset to a fresh playable state."""
        self.player = Player()
        self.falling: list[FallingObject] = []
        self.score = 0
        self.lives = settings.START_LIVES
        self.game_over = False
        self.new_record = False
        self.effects = EffectTimer()

    @property
    def level(self) -> int:
        """Difficulty level derived from score, capped at ``MAX_LEVEL``."""
        return min(settings.MAX_LEVEL, self.score // settings.POINTS_PER_LEVEL)

    def handle_events(self) -> bool:
        """Process window events. Returns False when the app should quit."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if self.game_over and event.key == pygame.K_r:
                    self.reset()
        return True

    def update(self) -> None:
        if self.game_over:
            return

        # Move player from held keys.
        keys = pygame.key.get_pressed()
        dx = 0
        if keys[pygame.K_LEFT]:
            dx -= settings.PLAYER_SPEED
        if keys[pygame.K_RIGHT]:
            dx += settings.PLAYER_SPEED
        self.player.move(dx)

        # Apply timed power-up effects to the player and the world.
        self.player.set_wide(self.effects.active("wide"))
        speed_scale = (
            settings.SLOWMO_SPEED_SCALE if self.effects.active("slowmo") else 1.0
        )
        magnet = self.effects.active("magnet")

        # Occasionally spawn a new falling object (chance, speed and bomb
        # share all grow with the current difficulty level).
        if random.random() < settings.spawn_chance_for_level(self.level):
            self.falling.append(spawn_falling_object(self.level))

        # Move objects and resolve collisions.
        for obj in list(self.falling):
            obj.update(speed_scale)
            if magnet and not obj.harmful:
                self._apply_magnet(obj)
            if obj.rect.colliderect(self.player.rect):
                self.falling.remove(obj)
                if obj.harmful:
                    self.lives -= 1
                    self._play("bomb")
                elif isinstance(obj, PowerUp):
                    self.effects.activate(obj.effect_key, obj.duration)
                    self._play("catch")
                else:
                    self.score += obj.points
                    self._play("catch")
            elif obj.off_screen():
                self.falling.remove(obj)
                if obj.penalize_on_miss:
                    # Missed a collectible.
                    self.lives -= 1

        if self.lives <= 0:
            self.lives = 0
            self.game_over = True
            self.new_record = self.highscores.submit(self.score)
            self._play("gameover")

    def _play(self, key: str) -> None:
        """Play a named sound if audio is available; never raises."""
        sound = assets.sound(key)
        if sound is not None:
            sound.play()

    def _apply_magnet(self, obj: FallingObject) -> None:
        """Slide a harmless object toward the paddle within ``MAGNET_RANGE``."""
        gap = self.player.rect.top - obj.rect.bottom
        if gap > settings.MAGNET_RANGE or gap < -self.player.rect.height:
            return
        pull = settings.MAGNET_PULL
        delta = self.player.rect.centerx - obj.rect.centerx
        if abs(delta) <= pull:
            obj.rect.centerx = self.player.rect.centerx
        else:
            obj.rect.centerx += pull if delta > 0 else -pull

    def draw(self) -> None:
        self.screen.fill(settings.BG_COLOR)
        for obj in self.falling:
            obj.draw(self.screen, self.font)
        self.player.draw(self.screen)

        hud = self.font.render(
            f"Score: {self.score}   Lives: {self.lives}   "
            f"Best: {self.highscores.best()}   Lv: {self.level}",
            True,
            settings.HUD_COLOR,
        )
        self.screen.blit(hud, (12, 12))
        self._draw_active_effects()

        if self.game_over:
            self._draw_game_over()

        pygame.display.flip()

    def _draw_active_effects(self) -> None:
        """List running power-up effects with their remaining seconds."""
        y = 44
        for key, remaining in self.effects.active_items():
            label = settings.POWERUP_LABELS.get(key, key)
            text = self.font.render(
                f"{label}  {remaining:.1f}s", True, settings.TEXT_COLOR
            )
            self.screen.blit(text, (12, y))
            y += text.get_height() + 4

    def _draw_game_over(self) -> None:
        overlay = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
        overlay.set_alpha(160)
        overlay.fill(settings.BG_COLOR)
        self.screen.blit(overlay, (0, 0))

        over = self.font.render("GAME OVER", True, settings.TEXT_COLOR)
        lines = [over]
        if self.new_record:
            lines.append(
                self.font.render(
                    f"NEW HIGH SCORE: {self.score}", True, settings.GOLDEN_COLOR
                )
            )
        lines.append(self.font.render("Press R to restart", True, settings.TEXT_COLOR))
        cx = settings.SCREEN_WIDTH // 2
        y = settings.SCREEN_HEIGHT // 2 - 40
        for line in lines:
            self.screen.blit(line, (cx - line.get_width() // 2, y))
            y += line.get_height() + 8

    def run(self) -> None:
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(settings.FPS)
        pygame.quit()
