"""Procedurally generate every sprite and sound used by the game.

Run from anywhere with:  python tools/generate_assets.py

All output lands in ``assets/`` and is released under CC0 (see
``assets/CREDITS.md``). Re-running the script overwrites the files, so the
whole asset pack can be reproduced from source alone.
"""
import math
import random
import struct
import wave
from pathlib import Path

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SPRITE_DIR = ROOT / "assets" / "sprites"
SOUND_DIR = ROOT / "assets" / "sounds"

SAMPLE_RATE = 44100

# Keep these in sync with src/settings.py colors.
COLORS = {
    "player": (86, 200, 255),
    "item": (255, 200, 87),
    "golden": (255, 215, 0),
    "bomb": (230, 90, 90),
    "wide": (120, 255, 160),
    "magnet": (200, 130, 255),
    "slowmo": (130, 220, 255),
}
LETTERS = {"wide": "W", "magnet": "M", "slowmo": "S"}


def _darker(color, factor=0.65):
    return tuple(round(c * factor) for c in color)


def make_collectible(key: str, surface_size=48) -> pygame.Surface:
    """Circle with outline and highlight; golden gets a stem + sparkles."""
    surf = pygame.Surface((surface_size, surface_size), pygame.SRCALPHA)
    color = COLORS[key]
    center = (surface_size // 2, surface_size // 2 + 3)
    pygame.draw.circle(surf, color, center, 16)
    pygame.draw.circle(surf, _darker(color), center, 16, 2)
    pygame.draw.circle(surf, (255, 255, 255, 150), (center[0] - 6, center[1] - 7), 4)
    if key == "golden":
        pygame.draw.line(surf, (139, 69, 19), (center[0], center[1] - 16),
                         (center[0] + 4, center[1] - 22), 3)
        for px, py in ((8, 10), (38, 16)):
            pygame.draw.circle(surf, (255, 255, 220, 200), (px, py), 2)
    if key == "bomb":
        pygame.draw.line(surf, (110, 70, 35), (center[0], center[1] - 16),
                         (center[0] + 7, center[1] - 24), 3)
        pygame.draw.circle(surf, (255, 230, 90), (center[0] + 8, center[1] - 25), 3)
    return surf


def make_powerup(key: str, surface_size=48) -> pygame.Surface:
    """Rounded plate with white border and a letter, matching the HUD style."""
    surf = pygame.Surface((surface_size, surface_size), pygame.SRCALPHA)
    plate = pygame.Rect(6, 6, surface_size - 12, surface_size - 12)
    pygame.draw.rect(surf, COLORS[key], plate, border_radius=10)
    pygame.draw.rect(surf, (255, 255, 255), plate, 3, border_radius=10)
    font = pygame.font.Font(None, 30)
    text = font.render(LETTERS[key], True, (20, 20, 30))
    surf.blit(text, text.get_rect(center=plate.center))
    return surf


def make_player(surface_size=(128, 36)) -> pygame.Surface:
    surf = pygame.Surface(surface_size, pygame.SRCALPHA)
    body = surf.get_rect()
    pygame.draw.rect(surf, COLORS["player"], body, border_radius=10)
    pygame.draw.rect(surf, _darker(COLORS["player"]), body, 3, border_radius=10)
    strip = pygame.Rect(6, 5, surface_size[0] - 12, 5)
    pygame.draw.rect(surf, (255, 255, 255, 120), strip, border_radius=3)
    return surf


def write_wav(name: str, samples: list) -> None:
    frames = b"".join(
        struct.pack("<h", int(max(-1.0, min(1.0, s)) * 32767)) for s in samples
    )
    with wave.open(str(SOUND_DIR / name), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(SAMPLE_RATE)
        wav.writeframes(frames)


def tone(freq: float, seconds: float, decay: float = 4.0, gain: float = 0.5):
    n = int(SAMPLE_RATE * seconds)
    return [
        math.sin(2 * math.pi * freq * i / SAMPLE_RATE)
        * math.exp(-decay * i / SAMPLE_RATE)
        * gain
        for i in range(n)
    ]


def main() -> None:
    pygame.font.init()
    SPRITE_DIR.mkdir(parents=True, exist_ok=True)
    SOUND_DIR.mkdir(parents=True, exist_ok=True)

    sprites = {"item": make_collectible("item"), "golden": make_collectible("golden"),
               "bomb": make_collectible("bomb"), "player": make_player()}
    for key in ("wide", "magnet", "slowmo"):
        sprites[key] = make_powerup(key)
    for key, surf in sprites.items():
        pygame.image.save(surf, str(SPRITE_DIR / f"{key}.png"))

    rng = random.Random(2026)
    catch = tone(660, 0.07) + tone(990, 0.09)
    bomb, acc = [], 0.0
    for _ in range(int(SAMPLE_RATE * 0.28)):
        acc = 0.72 * acc + 0.28 * rng.uniform(-1.0, 1.0)
        bomb.append(acc * math.exp(-7 * len(bomb) / SAMPLE_RATE) * 0.9)
    gameover = tone(440, 0.16) + tone(330, 0.16) + tone(220, 0.3, decay=3.0)

    write_wav("catch.wav", catch)
    write_wav("bomb.wav", bomb)
    write_wav("gameover.wav", gameover)

    print("sprites:", sorted(p.name for p in SPRITE_DIR.glob("*.png")))
    print("sounds: ", sorted(p.name for p in SOUND_DIR.glob("*.wav")))


if __name__ == "__main__":
    main()
