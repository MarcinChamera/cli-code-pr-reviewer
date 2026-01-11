# CLAUDE.md

This file provides guidance to Claude Code when working with this repository.

## Project Overview

Antigravity Snake - A Python/Pygame Snake game with dynamic Mandelbrot set and fireworks backgrounds, Roman-style decorative UI.

## Commands

### Run the Game
```bash
source .venv/bin/activate && python snake.py
```

### Install Dependencies
```bash
pip install pygame numpy
```

## Architecture

### Main Files
- **snake.py** - Complete game implementation (~486 lines)
  - Game loop with state management (game_over, game_close, game_won)
  - Snake movement with arrow key controls
  - Collision detection (walls, self)
  - Score and time tracking

### Background Systems
1. **Mandelbrot Set** (`render_mandelbrot_background`)
   - Uses NumPy for performant pixel manipulation
   - RENDER_SCALE=6 for performance optimization
   - Constant zooming animation (mandelbrot_zoom_speed=1.003)
   - MAX_ITER=64, resets when zoom > 1e10

2. **Fireworks Animation** (`FireworksManager`, `Rocket`, `FireworkParticle`)
   - Particle system with gravity and decay
   - Rocket trails and explosion effects
   - Auto-spawns rockets every 40 frames

### Game Progression
- Start with Mandelbrot background
- After 5 apples eaten: switch to Fireworks
- After 5 more apples (total 10): victory screen
- Speed increases every 5 apples

### UI Elements
- **Roman/Gothic Border** (`draw_roman_border`)
  - Gold and dark brown color scheme
  - Corner ornaments and rose decorations
  - BORDER_PADDING=50px for play area

- **Score Display** (`show_score`)
  - Left side panel: Score, Time, Background name, Progress
  - Georgia font with gold colors

### Constants
- WIDTH=1200, HEIGHT=900
- BLOCK_SIZE=30 (snake segment size)
- SPEED=12 (base game speed)
- BORDER_PADDING=50 (decorative border width)

## GitHub Actions Workflows

### claude.yml
- Owner-only execution (github.actor == github.repository_owner)
- Triggers: issue_comment, pull_request_review_comment, issues, pull_request_review
- Permissions: contents, pull-requests, issues, id-token, actions

### claude-code-review.yml
- Auto-runs on PR events (opened, synchronize, ready_for_review, reopened)
- Uses code-review plugin for automated PR review
- Permissions: contents, pull-requests, issues, id-token

## Key Technical Details

- NumPy array operations for Mandelbrot rendering
- pygame.surfarray.blit_array for fast surface updates
- Python global variables for game state (current_background, mandelbrot_zoom)
- Recursive game_loop() call for restart (game_loop() inside game_loop)
