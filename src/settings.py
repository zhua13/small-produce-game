"""Central configuration for the game: screen, colors, and gameplay tuning.

Keeping constants in one place makes it easy to balance the game later and
lets other modules import a single source of truth.
"""

# --- Screen ---
SCREEN_WIDTH = 480
SCREEN_HEIGHT = 640
FPS = 60
CAPTION = "Falling Catch"

# --- Colors (R, G, B) ---
BG_COLOR = (18, 18, 32)
PLAYER_COLOR = (86, 200, 255)
ITEM_COLOR = (255, 200, 87)
BOMB_COLOR = (230, 90, 90)
GOLDEN_COLOR = (255, 215, 0)
TEXT_COLOR = (240, 240, 240)
HUD_COLOR = (150, 230, 150)

# --- Player ---
PLAYER_WIDTH = 70
PLAYER_HEIGHT = 20
PLAYER_SPEED = 7

# --- Falling objects ---
ITEM_SIZE = 22
ITEM_FALL_SPEED = 3
SPAWN_CHANCE = 0.035  # probability per frame of spawning a new object
GOLDEN_SCORE_MULTIPLIER = 2

# Relative spawn weights per object type; resolved by ``spawn_falling_object``.
# Keys must match the ``type_key`` values in ``entities.FALLING_TYPES``.
SPAWN_WEIGHTS = {
    "item": 0.55,
    "bomb": 0.25,
    "golden": 0.11,
    "wide": 0.03,
    "magnet": 0.03,
    "slowmo": 0.03,
}

# --- Power-ups ---
WIDE_COLOR = (120, 255, 160)
MAGNET_COLOR = (200, 130, 255)
SLOWMO_COLOR = (130, 220, 255)
WIDE_FACTOR = 1.8          # paddle width multiplier while "wide" is active
MAGNET_RANGE = 140         # px above the paddle where pulling happens
MAGNET_PULL = 6            # px per frame an object slides toward the paddle
SLOWMO_SPEED_SCALE = 0.4   # falling-object speed multiplier during slow-mo
POWERUP_DURATION_MS = 6000
SLOWMO_DURATION_MS = 4000
POWERUP_LABELS = {"wide": "WIDE PADDLE", "magnet": "MAGNET", "slowmo": "SLOW-MO"}

# --- Difficulty curve ---
# Every POINTS_PER_LEVEL caught points raises the level by one; the level
# drives spawn chance, fall speed and bomb weight until MAX_LEVEL is reached.
POINTS_PER_LEVEL = 10
MAX_LEVEL = 10
SPAWN_CHANCE_PER_LEVEL = 0.006  # extra spawn probability per level
FALL_SPEED_PER_LEVEL = 1        # extra px/frame per level (int steps keep
                                # pygame.Rect integer coordinates exact)
BOMB_WEIGHT_PER_LEVEL = 0.02    # extra relative bomb weight per level


def spawn_chance_for_level(level: int) -> float:
    """Spawn probability per frame at the given difficulty level."""
    return SPAWN_CHANCE + SPAWN_CHANCE_PER_LEVEL * max(0, level)


# --- Game state ---
START_LIVES = 3
