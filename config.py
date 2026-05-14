"""
Game Configuration and Constants
"""

import pygame

pygame.init()

# =========================
# DISPLAY CONFIG
# =========================
TILE_SIZE = 28
ROWS = 21
COLS = 19

WIDTH = COLS * TILE_SIZE
MAZE_HEIGHT = ROWS * TILE_SIZE
HUD_HEIGHT = 70
HEIGHT = MAZE_HEIGHT + HUD_HEIGHT

# =========================
# GAME TIMINGS
# =========================
FPS = 60
COUNTDOWN_SECONDS = 5
DEATH_DURATION = 90
FRIGHTENED_DURATION = 8 * FPS
GHOST_RELEASE_DELAY = FPS

# =========================
# COLORS (Retro Arcade Palette)
# =========================
BLACK = (0, 0, 0)
BLUE = (33, 33, 255)
BLUE_DARK = (0, 0, 120)
YELLOW = (255, 218, 0)
WHITE = (255, 255, 255)
PELLET = (255, 184, 222)
POWER_PELLET = (255, 240, 255)
RED = (255, 45, 45)
CYAN = (0, 255, 255)
PINK = (255, 105, 180)
FRIGHTENED_BLUE = (40, 90, 255)
GHOST_BLUE = (80, 210, 255)
GHOST_ORANGE = (255, 170, 45)
HUD_TEXT = (255, 236, 153)

# =========================
# FONTS
# =========================
FONT = pygame.font.SysFont("consolas", 22, bold=True)
SMALL_FONT = pygame.font.SysFont("consolas", 14, bold=True)
TITLE_FONT = pygame.font.SysFont("consolas", 24, bold=True)

# =========================
# DIRECTIONS
# =========================
DIRECTIONS = {
    "right": pygame.Vector2(1, 0),
    "left": pygame.Vector2(-1, 0),
    "up": pygame.Vector2(0, -1),
    "down": pygame.Vector2(0, 1),
}

# =========================
# GHOST CONFIGURATION
# =========================
GHOSTS_CONFIG = [
    {
        "name": "A*",
        "algorithm": "astar",
        "color": RED,
        "initial_tile": (9, 9),
        "speed": 0.062,
        "release_at": 0,
    },
    {
        "name": "BFS",
        "algorithm": "bfs",
        "color": GHOST_BLUE,
        "initial_tile": (10, 9),
        "speed": 0.055,
        "release_at": 30,
    },
    {
        "name": "DIJK",
        "algorithm": "dijkstra",
        "color": GHOST_ORANGE,
        "initial_tile": (11, 9),
        "speed": 0.06,
        "release_at": 60,
    },

]

# =========================
# PLAYER CONFIG
# =========================
PLAYER_RADIUS = 11
PLAYER_SPEED = 0.105
PLAYER_START_TILE = None  # Will be set from map parsing
