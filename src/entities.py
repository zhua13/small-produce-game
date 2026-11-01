"""Game entities: the player paddle and falling objects.

These are plain data + behavior classes that operate on pygame.Rect, so they
stay independent of the rendering/loop logic in ``game.py``. Falling objects
form a small type hierarchy (Item / Bomb / GoldenApple / power-ups) created
through the weighted ``spawn_falling_object`` factory. Timed power-up effects
are tracked centrally by ``EffectTimer``.
"""
import random

import pygame

from . import assets, settings


class Player:
    """The controllable paddle at the bottom of the screen."""

    def __init__(self) -> None:
        self.rect = pygame.Rect(
            settings.SCREEN_WIDTH // 2 - settings.PLAYER_WIDTH // 2,
            settings.SCREEN_HEIGHT - 40,
            settings.PLAYER_WIDTH,
            settings.PLAYER_HEIGHT,
        )

    def move(self, dx: int) -> None:
        """Move horizontally by ``dx`` pixels, clamped to the screen edges."""
        self.rect.x += dx
        self._clamp()

    def set_wide(self, wide: bool) -> None:
        """Grow or shrink the paddle to the wide-effect width.

        The paddle center stays put so the effect feels symmetric, then the
        resized rect is clamped back into the screen.
        """
        target = round(settings.PLAYER_WIDTH * (settings.WIDE_FACTOR if wide else 1.0))
        if self.rect.width == target:
            return
        center_x, center_y = self.rect.center
        self.rect.width = target
        self.rect.center = center_x, center_y
        self._clamp()

    def _clamp(self) -> None:
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > settings.SCREEN_WIDTH:
            self.rect.right = settings.SCREEN_WIDTH

    def draw(self, surface: pygame.Surface) -> None:
        sprite = assets.scaled_image("player", self.rect.size)
        if sprite is not None:
            surface.blit(sprite, self.rect.topleft)
        else:
            pygame.draw.rect(surface, settings.PLAYER_COLOR, self.rect, border_radius=6)


class EffectTimer:
    """Track active timed effects as ``key -> expiry timestamp (ms)``.

    Uses ``pygame.time.get_ticks()`` so all power-up durations share one
    clock; remaining times are surfaced to the HUD every frame.
    """

    def __init__(self) -> None:
        self._expires_at: dict[str, int] = {}

    def activate(self, key: str, duration_ms: int) -> None:
        """(Re)start an effect; picking up the same power-up refreshes it."""
        self._expires_at[key] = pygame.time.get_ticks() + duration_ms

    def remaining(self, key: str) -> float:
        deadline = self._expires_at.get(key)
        if deadline is None:
            return 0.0
        return max(0.0, (deadline - pygame.time.get_ticks()) / 1000.0)

    def active(self, key: str) -> bool:
        return self.remaining(key) > 0

    def active_items(self) -> list[tuple[str, float]]:
        """Currently running effects as ``(key, seconds_left)`` pairs."""
        return [
            (key, remaining)
            for key, remaining in ((k, self.remaining(k)) for k in self._expires_at)
            if remaining > 0
        ]

    def clear(self) -> None:
        self._expires_at.clear()


class FallingObject:
    """Base class for a falling object.

    Subclasses describe themselves through class attributes only:

    * ``type_key`` – identifier used by the spawn weights in settings
    * ``color``    – rendering color
    * ``points``   – score added when caught (0 for harmful objects)
    * ``harmful``  – catching it costs a life (bombs)
    * ``penalize_on_miss`` – letting it fall off screen costs a life
      (collectibles only; power-ups are not punished when missed)
    """

    type_key: str = ""
    color: tuple[int, int, int] = (255, 255, 255)
    points: int = 0
    harmful: bool = False
    penalize_on_miss: bool = False

    def __init__(self) -> None:
        size = settings.ITEM_SIZE
        self.rect = pygame.Rect(
            random.randint(0, settings.SCREEN_WIDTH - size),
            -size,
            size,
            size,
        )
        self.speed = settings.ITEM_FALL_SPEED

    def update(self, speed_scale: float = 1.0) -> None:
        self.rect.y += self.speed * speed_scale

    def off_screen(self) -> bool:
        return self.rect.top > settings.SCREEN_HEIGHT

    def draw(
        self, surface: pygame.Surface, font: "pygame.font.Font | None" = None
    ) -> None:
        sprite = assets.scaled_image(self.type_key, self.rect.size)
        if sprite is not None:
            surface.blit(sprite, self.rect.topleft)
        else:
            pygame.draw.rect(surface, self.color, self.rect, border_radius=4)


class Item(FallingObject):
    """A regular collectible worth one point."""

    type_key = "item"
    color = settings.ITEM_COLOR
    points = 1
    penalize_on_miss = True


class Bomb(FallingObject):
    """Harmful object: catching it costs a life."""

    type_key = "bomb"
    color = settings.BOMB_COLOR
    harmful = True


class GoldenApple(FallingObject):
    """Rare collectible worth ``GOLDEN_SCORE_MULTIPLIER`` times an item."""

    type_key = "golden"
    color = settings.GOLDEN_COLOR
    points = settings.GOLDEN_SCORE_MULTIPLIER
    penalize_on_miss = True


class PowerUp(FallingObject):
    """Base class for falling power-ups.

    Catching one never scores; instead it activates the effect named by
    ``effect_key`` for ``duration`` milliseconds.
    """

    effect_key: str = ""
    label: str = "?"
    duration: int = settings.POWERUP_DURATION_MS

    def draw(
        self, surface: pygame.Surface, font: "pygame.font.Font | None" = None
    ) -> None:
        sprite = assets.scaled_image(self.type_key, self.rect.size)
        if sprite is not None:
            surface.blit(sprite, self.rect.topleft)
            return
        pygame.draw.rect(surface, self.color, self.rect, border_radius=4)
        pygame.draw.rect(surface, settings.TEXT_COLOR, self.rect, 2, border_radius=4)
        if font is not None:
            text = font.render(self.label, True, settings.BG_COLOR)
            surface.blit(text, text.get_rect(center=self.rect.center))


class WidePaddle(PowerUp):
    """Temporarily widens the player paddle."""

    type_key = "wide"
    effect_key = "wide"
    color = settings.WIDE_COLOR
    label = "W"


class MagnetPull(PowerUp):
    """Temporarily pulls collectibles toward the paddle."""

    type_key = "magnet"
    effect_key = "magnet"
    color = settings.MAGNET_COLOR
    label = "M"


class SlowMotion(PowerUp):
    """Temporarily slows every falling object down."""

    type_key = "slowmo"
    effect_key = "slowmo"
    color = settings.SLOWMO_COLOR
    label = "S"
    duration = settings.SLOWMO_DURATION_MS


# Registry used by the weighted spawner; keep in sync with settings.SPAWN_WEIGHTS.
FALLING_TYPES: dict[str, type[FallingObject]] = {
    cls.type_key: cls
    for cls in (Item, Bomb, GoldenApple, WidePaddle, MagnetPull, SlowMotion)
}


def spawn_falling_object(level: int = 0) -> FallingObject:
    """Create one falling object for the current difficulty level.

    Base weights come from ``settings.SPAWN_WEIGHTS``; each level adds
    ``BOMB_WEIGHT_PER_LEVEL`` to the bomb share and speeds everything up.
    """
    level = max(0, level)
    keys = list(FALLING_TYPES)
    weights = [
        settings.SPAWN_WEIGHTS[k]
        + (settings.BOMB_WEIGHT_PER_LEVEL * level if k == "bomb" else 0.0)
        for k in keys
    ]
    chosen = random.choices(keys, weights=weights, k=1)[0]
    obj = FALLING_TYPES[chosen]()
    obj.speed += settings.FALL_SPEED_PER_LEVEL * level
    return obj
