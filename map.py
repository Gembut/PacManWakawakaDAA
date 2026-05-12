"""
Map parsing and tile utilities
"""

import pygame
from config import TILE_SIZE, ROWS, COLS, WIDTH, MAZE_HEIGHT, DIRECTIONS

# =========================
# MAP LEGEND
# =========================
# # = Wall
# . = Pellet
# o = Power Pellet
# P = Player Spawn
# = = Ghost cage door
# Empty space = Path

GAME_MAP = [
    "###################",
    "#o.......#.......o#",
    "#.###.###.#.###.###",
    "#o...............o#",
    "#.###.#.#####.#.###",
    "#.....#...#...#...#",
    "#####.### # ###.###",
    "    #.#       #.#  ",
    "#####.# ##=## #.###",
    "     .  #   #  .   ",
    "#####.# ## ## #.###",
    "    #.#       #.#  ",
    "#####.# ##### #.###",
    "#........#........#",
    "#.###.###.#.###.###",
    "#...#.....P.....#.#",
    "###.#.#.#####.#.#.#",
    "#.....#...#...#...#",
    "#.#######.#.#######",
    "#o...............o#",
    "###################",
]


def parse_game_map(rows):
    """Parse game map into walls, pellets, power pellets, and player spawn"""
    parsed_walls = []
    parsed_pellets = set()
    parsed_power_pellets = set()
    parsed_player_start_tile = None

    for row_index, row in enumerate(rows):
        for col_index, tile in enumerate(row):
            if tile == "#":
                parsed_walls.append(
                    pygame.Rect(
                        col_index * TILE_SIZE,
                        row_index * TILE_SIZE,
                        TILE_SIZE,
                        TILE_SIZE,
                    )
                )
            elif tile == ".":
                parsed_pellets.add((col_index, row_index))
            elif tile == "o":
                parsed_power_pellets.add((col_index, row_index))
            elif tile == "P":
                parsed_player_start_tile = (col_index, row_index)

    return parsed_walls, parsed_pellets, parsed_power_pellets, parsed_player_start_tile


def tile_center(tile):
    """Get the pixel center of a tile"""
    col, row = tile
    return pygame.Vector2(
        col * TILE_SIZE + TILE_SIZE // 2,
        row * TILE_SIZE + TILE_SIZE // 2,
    )


def map_tile(tile):
    """Get the character at a given tile coordinate"""
    col, row = tile
    if row < 0 or row >= ROWS or col < 0 or col >= COLS:
        return "#"

    if col >= len(GAME_MAP[row]):
        return " "

    return GAME_MAP[row][col]


def is_walkable(tile):
    """Check if a tile is walkable for the player"""
    return map_tile(tile) not in ["#", "="]


def is_ghost_walkable(tile):
    """Check if a tile is walkable for ghosts"""
    return map_tile(tile) != "#"


def wrap_tile(tile):
    """Wrap tile coordinates using modulo"""
    col, row = tile
    return (col % COLS, row % ROWS)


def next_tile(tile, move_direction):
    """Get the next tile in a given direction"""
    return (
        tile[0] + int(move_direction.x),
        tile[1] + int(move_direction.y),
    )


def is_wrap_move(tile, move_direction):
    """Check if a move would wrap around the map"""
    candidate = next_tile(tile, move_direction)
    return (
        candidate[0] < 0
        or candidate[0] >= COLS
        or candidate[1] < 0
        or candidate[1] >= ROWS
    )


def offscreen_target(tile, move_direction):
    """Get the offscreen target position for wrapping moves"""
    col, row = tile
    x = col * TILE_SIZE + TILE_SIZE // 2
    y = row * TILE_SIZE + TILE_SIZE // 2

    if move_direction.x > 0:
        x = WIDTH + TILE_SIZE // 2
    elif move_direction.x < 0:
        x = -TILE_SIZE // 2
    elif move_direction.y > 0:
        y = MAZE_HEIGHT + TILE_SIZE // 2
    elif move_direction.y < 0:
        y = -TILE_SIZE // 2

    return pygame.Vector2(x, y)


def wrapped_step_direction(start, target):
    """Get the direction to move for wrapped tiles"""
    if start[0] == COLS - 1 and target[0] == 0:
        return DIRECTIONS["right"]
    if start[0] == 0 and target[0] == COLS - 1:
        return DIRECTIONS["left"]
    if start[1] == ROWS - 1 and target[1] == 0:
        return DIRECTIONS["down"]
    if start[1] == 0 and target[1] == ROWS - 1:
        return DIRECTIONS["up"]

    return pygame.Vector2(target[0] - start[0], target[1] - start[1])


def ghost_neighbors(tile):
    """Get valid neighbor tiles for a ghost"""
    neighbors = []
    for move_direction in DIRECTIONS.values():
        candidate = wrap_tile(next_tile(tile, move_direction))
        if is_ghost_walkable(candidate):
            neighbors.append(candidate)

    return neighbors
