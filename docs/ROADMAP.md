# Roadmap

This document tracks the development plan for **Small Produce**, an open
arcade game collection built with Python and Pygame. Milestones are delivered
incrementally; completed items are checked off in the release notes.

## v0.1.0 — Gameplay Depth (November 2026)

Make the launch title *Falling Catch* more than a tech demo.

- [x] Refactor `FallingObject` into a typed hierarchy
  (normal item / bomb / golden apple with 2× score)
- [x] Weighted random spawning for object types
- [x] Timed power-ups:
  - [x] Wide paddle
  - [x] Item magnet
  - [x] Slow motion
- [x] Power-up effect indicators in the HUD
- [x] High-score persistence (local JSON save file)
- [x] Unit tests for player movement and collision logic

## v0.2.0 — Difficulty & Presentation (December 2026)

Scale the challenge and replace placeholder visuals.

- [x] Difficulty curve: spawn rate, fall speed and bomb ratio scale
  with score, shown as a "Level" indicator
- [x] Sprite art for player and falling objects (CC0 assets, credited
  in `assets/CREDITS.md`)
- [x] Sound effects: catch, bomb hit, game over
- [ ] Pause menu and settings screen (volume toggle, paddle sensitivity)
- [ ] Initial issue tracker usage and a `CHANGELOG.md`

## v0.3.0 — Multi-Game Architecture (January 2027)

Grow into an actual game *collection* rather than a single game.

- [ ] Extract a `Scene` state-machine base class
  (menu / game / game over) and migrate *Falling Catch* onto it
- [ ] Add a second mini-game (Snake or Dodger) reusing the
  `settings / entities / game` layering
- [ ] Main menu with game selection
- [ ] Per-game high-score leaderboards
- [ ] CI pipeline (GitHub Actions: lint + `pytest` on every push)
- [ ] `CONTRIBUTING.md` and beginner-friendly issue labels

## Later Ideas

No schedule yet — contributions and feedback are welcome on these:

- Online leaderboard between players
- Controller (gamepad) support
- Level editor for custom falling patterns
- Packaging as a standalone executable (PyInstaller)

---

*Last updated: 2026-11-02. See also the [README](../README.md).*
