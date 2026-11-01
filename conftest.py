"""Root conftest: force headless SDL drivers before any pygame import.

Living at the project root also makes pytest put this directory on
sys.path, so tests can ``from src...`` import directly.
"""
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
