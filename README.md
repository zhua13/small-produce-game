# Small Produce

A small arcade game collection built with **Python** and **Pygame**. The
current playable title is **Falling Catch** — move the paddle to catch good
items and dodge bombs.

## Features

- Playable catch-the-item arcade loop at 60 FPS
- Score and lives HUD, game-over and restart flow
- Clean separation between settings, entities and the game loop, so new
  mini-games can be added without rewriting the core

## Requirements

- Python 3.10+
- Pygame 2.5+

## Getting started

```bash
# create an isolated environment (recommended)
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

# install dependencies
pip install -r requirements.txt

# run the game
python main.py
```

## Controls

| Key | Action |
| --- | --- |
| `←` / `→` | Move the paddle |
| `R` | Restart after game over |
| `Esc` | Quit |

## Project layout

```
small_produce/
├── main.py            # entry point
├── src/
│   ├── settings.py    # constants & tuning
│   ├── assets.py      # sprite/sound loading with flat-color fallback
│   ├── entities.py    # Player, falling objects, power-ups, effects
│   ├── storage.py     # high-score persistence (JSON, stored in user home)
│   └── game.py        # Game loop, input, collisions, rendering
├── assets/            # generated sprites & sounds (CC0, see CREDITS.md)
├── tools/             # generate_assets.py — rebuilds the whole asset pack
├── tests/             # headless pytest suite
└── requirements.txt
```

## Development

```bash
pip install -r requirements.txt -r requirements-dev.txt

pytest          # run the test suite (headless, safe for CI)
python main.py  # play the game
```

High scores are kept in `~/.small_produce/highscores.json`, outside the
repository, so clone dirs stay clean.

## Roadmap

Development is planned in versioned milestones (v0.1.0 gameplay depth,
v0.2.0 difficulty & presentation, v0.3.0 multi-game architecture).
See [`docs/ROADMAP.md`](docs/ROADMAP.md) for the full plan.

## License

Distributed under the MIT License. See [`LICENSE`](LICENSE) for details.
