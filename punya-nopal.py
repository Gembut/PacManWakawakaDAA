import heapq
import math
import sys
from collections import deque

import pygame

pygame.init()

# =========================
# CONFIG
# =========================
TILE_SIZE = 28
ROWS = 21
COLS = 19

WIDTH = COLS * TILE_SIZE
MAZE_HEIGHT = ROWS * TILE_SIZE
HUD_HEIGHT = 70
HEIGHT = MAZE_HEIGHT + HUD_HEIGHT

SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pac-Man Retro")

CLOCK = pygame.time.Clock()
FPS = 60
COUNTDOWN_SECONDS = 3
DEATH_DURATION = 90
FRIGHTENED_DURATION = 8 * FPS

# Retro arcade palette
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

FONT = pygame.font.SysFont("consolas", 22, bold=True)
SMALL_FONT = pygame.font.SysFont("consolas", 14, bold=True)
TITLE_FONT = pygame.font.SysFont("consolas", 24, bold=True)

DIRECTIONS = {
    "right": pygame.Vector2(1, 0),
    "left": pygame.Vector2(-1, 0),
    "up": pygame.Vector2(0, -1),
    "down": pygame.Vector2(0, 1),
}

# =========================
# MAP LEGEND
# # = Wall
# . = Pellet
# o = Power Pellet
# P = Player Spawn
# = = Ghost cage door
# Empty space = Path
# =========================
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
    parsed_walls = []
    parsed_pellets = set()
    parsed_power_pellets = set()
    parsed_player_start_tile = None

    for row_index, row in enumerate(rows):
        for col_index, tile in enumerate(row):
            if tile == "#":
                parsed_walls.append(pygame.Rect(
                    col_index * TILE_SIZE,
                    row_index * TILE_SIZE,
                    TILE_SIZE,
                    TILE_SIZE,
                ))
            elif tile == ".":
                parsed_pellets.add((col_index, row_index))
            elif tile == "o":
                parsed_power_pellets.add((col_index, row_index))
            elif tile == "P":
                parsed_player_start_tile = (col_index, row_index)

    return parsed_walls, parsed_pellets, parsed_power_pellets, parsed_player_start_tile

# =========================
# GAME STATE
# =========================
walls = []
pellets = set()
power_pellets = set()
player_start_tile = None

walls, pellets, power_pellets, player_start_tile = parse_game_map(GAME_MAP)

initial_pellets = pellets.copy()
initial_power_pellets = power_pellets.copy()

player_tile = player_start_tile
target_tile = player_start_tile
player_pos = pygame.Vector2(
    player_tile[0] * TILE_SIZE + TILE_SIZE // 2,
    player_tile[1] * TILE_SIZE + TILE_SIZE // 2,
)
start_pos = player_pos.copy()
target_pos = player_pos.copy()

player_radius = 11
step_progress = 1.0
step_speed = 0.105
wrapping_step = False

direction = pygame.Vector2(0, 0)
queued_direction = pygame.Vector2(0, 0)
facing_direction = pygame.Vector2(1, 0)

score = 0
lives = 3
pellets_eaten = 0
game_over = False
game_state = "countdown"
countdown_timer = COUNTDOWN_SECONDS * FPS
death_timer = 0
frightened_timer = 0
ghost_eat_score = 200

mouth_timer = 0
mouth_open = True

ghosts = [
    {
        "name": "A*",
        "algorithm": "astar",
        "color": RED,
        "initial_tile": (9, 9),
        "tile": (9, 9),
        "target_tile": (9, 9),
        "pos": pygame.Vector2(9 * TILE_SIZE + TILE_SIZE // 2, 9 * TILE_SIZE + TILE_SIZE // 2),
        "start_pos": pygame.Vector2(9 * TILE_SIZE + TILE_SIZE // 2, 9 * TILE_SIZE + TILE_SIZE // 2),
        "target_pos": pygame.Vector2(9 * TILE_SIZE + TILE_SIZE // 2, 9 * TILE_SIZE + TILE_SIZE // 2),
        "progress": 1.0,
        "speed": 0.062,
        "wrapping": False,
        "release_at": 0,
        "active": True,
        "eaten": False,
    },
    {
        "name": "BFS",
        "algorithm": "bfs",
        "color": GHOST_BLUE,
        "initial_tile": (10, 9),
        "tile": (10, 9),
        "target_tile": (10, 9),
        "pos": pygame.Vector2(10 * TILE_SIZE + TILE_SIZE // 2, 9 * TILE_SIZE + TILE_SIZE // 2),
        "start_pos": pygame.Vector2(10 * TILE_SIZE + TILE_SIZE // 2, 9 * TILE_SIZE + TILE_SIZE // 2),
        "target_pos": pygame.Vector2(10 * TILE_SIZE + TILE_SIZE // 2, 9 * TILE_SIZE + TILE_SIZE // 2),
        "progress": 1.0,
        "speed": 0.055,
        "wrapping": False,
        "release_at": 20,
        "active": False,
        "eaten": False,
    },
    {
        "name": "DIJK",
        "algorithm": "dijkstra",
        "color": GHOST_ORANGE,
        "initial_tile": (11, 9),
        "tile": (11, 9),
        "target_tile": (11, 9),
        "pos": pygame.Vector2(11 * TILE_SIZE + TILE_SIZE // 2, 9 * TILE_SIZE + TILE_SIZE // 2),
        "start_pos": pygame.Vector2(11 * TILE_SIZE + TILE_SIZE // 2, 9 * TILE_SIZE + TILE_SIZE // 2),
        "target_pos": pygame.Vector2(11 * TILE_SIZE + TILE_SIZE // 2, 9 * TILE_SIZE + TILE_SIZE // 2),
        "progress": 1.0,
        "speed": 0.06,
        "wrapping": False,
        "release_at": 45,
        "active": False,
        "eaten": False,
    },
]


# =========================
# HELPER FUNCTIONS
# =========================
def tile_center(tile):
    col, row = tile
    return pygame.Vector2(
        col * TILE_SIZE + TILE_SIZE // 2,
        row * TILE_SIZE + TILE_SIZE // 2,
    )


def map_tile(tile):
    col, row = tile
    if row < 0 or row >= ROWS or col < 0 or col >= COLS:
        return "#"

    if col >= len(GAME_MAP[row]):
        return " "

    return GAME_MAP[row][col]


def is_walkable(tile):
    return map_tile(tile) not in ["#", "="]


def is_ghost_walkable(tile):
    return map_tile(tile) != "#"


def wrap_tile(tile):
    col, row = tile
    return (col % COLS, row % ROWS)


def next_tile(tile, move_direction):
    return (
        tile[0] + int(move_direction.x),
        tile[1] + int(move_direction.y),
    )


def is_wrap_move(tile, move_direction):
    candidate = next_tile(tile, move_direction)
    return (
        candidate[0] < 0
        or candidate[0] >= COLS
        or candidate[1] < 0
        or candidate[1] >= ROWS
    )


def offscreen_target(tile, move_direction):
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
    neighbors = []
    for move_direction in DIRECTIONS.values():
        candidate = wrap_tile(next_tile(tile, move_direction))
        if is_ghost_walkable(candidate):
            neighbors.append(candidate)

    return neighbors


def reconstruct_path(came_from, start, goal):
    if goal not in came_from and goal != start:
        return []

    path = [goal]
    current = goal
    while current != start:
        current = came_from[current]
        path.append(current)

    path.reverse()
    return path


def grid_distance(first, second):
    dx = abs(first[0] - second[0])
    dy = abs(first[1] - second[1])
    return min(dx, COLS - dx) + min(dy, ROWS - dy)


def find_path_astar(start, goal):
    frontier = []
    heapq.heappush(frontier, (0, start))
    came_from = {}
    cost_so_far = {start: 0}

    while frontier:
        _, current = heapq.heappop(frontier)

        if current == goal:
            return reconstruct_path(came_from, start, goal)

        for neighbor in ghost_neighbors(current):
            new_cost = cost_so_far[current] + 1
            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = new_cost
                priority = new_cost + grid_distance(neighbor, goal)
                heapq.heappush(frontier, (priority, neighbor))
                came_from[neighbor] = current

    return []


def find_path_dijkstra(start, goal):
    frontier = []
    heapq.heappush(frontier, (0, start))
    came_from = {}
    cost_so_far = {start: 0}

    while frontier:
        current_cost, current = heapq.heappop(frontier)

        if current == goal:
            return reconstruct_path(came_from, start, goal)

        if current_cost > cost_so_far[current]:
            continue

        for neighbor in ghost_neighbors(current):
            new_cost = current_cost + 1
            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = new_cost
                heapq.heappush(frontier, (new_cost, neighbor))
                came_from[neighbor] = current

    return []


def find_path_bfs(start, goal):
    queue = deque([start])
    came_from = {}
    visited = {start}

    while queue:
        current = queue.popleft()

        if current == goal:
            return reconstruct_path(came_from, start, goal)

        for neighbor in ghost_neighbors(current):
            if neighbor not in visited:
                visited.add(neighbor)
                came_from[neighbor] = current
                queue.append(neighbor)

    return []


def find_ghost_path(ghost, goal):
    if ghost["algorithm"] == "astar":
        return find_path_astar(ghost["tile"], goal)

    if ghost["algorithm"] == "bfs":
        return find_path_bfs(ghost["tile"], goal)

    return find_path_dijkstra(ghost["tile"], goal)


def remaining_food():
    return len(pellets) + len(power_pellets)


def is_frightened():
    return frightened_timer > 0


def frightened_ghost_target(ghost):
    choices = ghost_neighbors(ghost["tile"])
    if not choices:
        return ghost["tile"]

    return max(choices, key=lambda tile: grid_distance(tile, player_tile))


def reset_ghost_position(ghost):
    ghost["tile"] = ghost["initial_tile"]
    ghost["target_tile"] = ghost["initial_tile"]
    ghost["pos"] = tile_center(ghost["initial_tile"])
    ghost["start_pos"] = ghost["pos"].copy()
    ghost["target_pos"] = ghost["pos"].copy()
    ghost["progress"] = 1.0
    ghost["wrapping"] = False
    ghost["eaten"] = False


def reset_round_positions():
    global player_tile, target_tile, player_pos, start_pos, target_pos, step_progress
    global direction, queued_direction, facing_direction, wrapping_step, frightened_timer, ghost_eat_score

    player_tile = player_start_tile
    target_tile = player_start_tile
    player_pos = tile_center(player_start_tile)
    start_pos = player_pos.copy()
    target_pos = player_pos.copy()
    step_progress = 1.0
    wrapping_step = False
    direction = pygame.Vector2(0, 0)
    queued_direction = pygame.Vector2(0, 0)
    facing_direction = pygame.Vector2(1, 0)
    frightened_timer = 0
    ghost_eat_score = 200

    for ghost in ghosts:
        reset_ghost_position(ghost)


def release_ghosts():
    for ghost in ghosts:
        if pellets_eaten >= ghost["release_at"]:
            ghost["active"] = True


def restart_game():
    global pellets, power_pellets
    global score, lives, pellets_eaten, game_over, game_state
    global countdown_timer, death_timer, frightened_timer, ghost_eat_score

    pellets = initial_pellets.copy()
    power_pellets = initial_power_pellets.copy()

    score = 0
    lives = 3
    pellets_eaten = 0
    game_over = False
    game_state = "countdown"
    countdown_timer = COUNTDOWN_SECONDS * FPS
    death_timer = 0
    frightened_timer = 0
    ghost_eat_score = 200

    reset_round_positions()
    for ghost in ghosts:
        ghost["active"] = pellets_eaten >= ghost["release_at"]


def start_countdown():
    global game_state, countdown_timer

    game_state = "countdown"
    countdown_timer = COUNTDOWN_SECONDS * FPS


def update_countdown():
    global game_state, countdown_timer

    countdown_timer -= 1
    if countdown_timer <= 0:
        game_state = "playing"


def update_death_animation():
    global death_timer, game_over, game_state

    death_timer += 1
    if death_timer < DEATH_DURATION:
        return

    if lives <= 0:
        game_over = True
        game_state = "game_over"
    else:
        reset_round_positions()
        release_ghosts()
        start_countdown()


def draw_background():
    SCREEN.fill(BLACK)

    for y in range(0, MAZE_HEIGHT, TILE_SIZE):
        pygame.draw.line(SCREEN, (6, 6, 22), (0, y), (WIDTH, y))

    for x in range(0, WIDTH, TILE_SIZE):
        pygame.draw.line(SCREEN, (6, 6, 22), (x, 0), (x, MAZE_HEIGHT))


def draw_walls():
    for wall in walls:
        pygame.draw.rect(SCREEN, BLUE, wall)
        inner = wall.inflate(-8, -8)
        pygame.draw.rect(SCREEN, BLUE_DARK, inner)
        pygame.draw.rect(SCREEN, CYAN, wall, 1)


def draw_ghost(center, color):
    x, y = center
    top = y - 13
    bottom = y + 12
    left = x - 11
    right = x + 11

    body_points = [
        (x, top),
        (x + 6, top + 2),
        (right, top + 9),
        (right, bottom - 5),
        (x + 8, bottom),
        (x + 4, bottom - 5),
        (x, bottom),
        (x - 4, bottom - 5),
        (x - 8, bottom),
        (left, bottom - 5),
        (left, top + 9),
        (x - 6, top + 2),
    ]

    shadow_points = [(px + 2, py + 2) for px, py in body_points]
    pygame.draw.polygon(SCREEN, (0, 0, 0), shadow_points)
    pygame.draw.polygon(SCREEN, color, body_points)
    pygame.draw.circle(SCREEN, color, (x, top + 11), 11)
    pygame.draw.rect(SCREEN, color, (left, top + 11, 22, 14))

    pygame.draw.line(SCREEN, WHITE, (x - 6, top + 3), (x - 1, top + 1), 2)

    pygame.draw.ellipse(SCREEN, WHITE, (x - 8, y - 8, 7, 9))
    pygame.draw.ellipse(SCREEN, WHITE, (x + 2, y - 8, 7, 9))
    pygame.draw.circle(SCREEN, BLUE_DARK, (x - 4, y - 4), 2)
    pygame.draw.circle(SCREEN, BLUE_DARK, (x + 6, y - 4), 2)

    pygame.draw.line(SCREEN, BLACK, (left + 2, bottom - 1), (right - 2, bottom - 1), 1)


def draw_ghost_eyes(center):
    x, y = center
    pygame.draw.ellipse(SCREEN, WHITE, (x - 9, y - 8, 8, 10))
    pygame.draw.ellipse(SCREEN, WHITE, (x + 2, y - 8, 8, 10))
    pygame.draw.circle(SCREEN, BLUE_DARK, (x - 4, y - 4), 2)
    pygame.draw.circle(SCREEN, BLUE_DARK, (x + 7, y - 4), 2)


def draw_ghost_cage():
    cage_rect = pygame.Rect(8 * TILE_SIZE, 8 * TILE_SIZE, 5 * TILE_SIZE, 3 * TILE_SIZE)
    inner_rect = cage_rect.inflate(-10, -8)
    door_rect = pygame.Rect(10 * TILE_SIZE, 8 * TILE_SIZE + 9, TILE_SIZE, 10)

    pygame.draw.rect(SCREEN, BLACK, inner_rect)
    pygame.draw.rect(SCREEN, BLUE, cage_rect, 4)
    pygame.draw.rect(SCREEN, CYAN, cage_rect.inflate(-5, -5), 1)

    pygame.draw.rect(SCREEN, PINK, door_rect)
    pygame.draw.line(SCREEN, WHITE, door_rect.topleft, door_rect.topright, 1)


def draw_pellets():
    for col, row in pellets:
        center = (
            col * TILE_SIZE + TILE_SIZE // 2,
            row * TILE_SIZE + TILE_SIZE // 2,
        )
        pygame.draw.circle(SCREEN, PELLET, center, 3)

    pulse = 1 + int((pygame.time.get_ticks() // 180) % 2)
    for col, row in power_pellets:
        center = (
            col * TILE_SIZE + TILE_SIZE // 2,
            row * TILE_SIZE + TILE_SIZE // 2,
        )
        pygame.draw.circle(SCREEN, POWER_PELLET, center, 7 + pulse)
        pygame.draw.circle(SCREEN, PINK, center, 4 + pulse)


def draw_hud():
    hud_y = MAZE_HEIGHT
    pygame.draw.rect(SCREEN, BLACK, (0, hud_y, WIDTH, HUD_HEIGHT))
    pygame.draw.line(SCREEN, BLUE, (0, hud_y), (WIDTH, hud_y), 3)
    pygame.draw.line(SCREEN, BLUE_DARK, (0, hud_y + 4), (WIDTH, hud_y + 4), 2)

    score_text = FONT.render(f"SCORE {score:04}", False, WHITE)
    title_text = TITLE_FONT.render("PAC-MAN", False, YELLOW)
    if is_frightened():
        move_text = SMALL_FONT.render(f"POWER {math.ceil(frightened_timer / FPS)}", False, FRIGHTENED_BLUE)
    else:
        move_text = SMALL_FONT.render("GRID MOVE: ARROWS / WASD", False, HUD_TEXT)
    lives_text = SMALL_FONT.render("LIVES", False, WHITE)

    SCREEN.blit(score_text, (14, hud_y + 12))
    SCREEN.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, hud_y + 8))
    SCREEN.blit(move_text, (WIDTH // 2 - move_text.get_width() // 2, hud_y + 40))
    SCREEN.blit(lives_text, (WIDTH - 122, hud_y + 14))

    for i in range(lives):
        x = WIDTH - 100 + i * 24
        y = hud_y + 42
        pygame.draw.circle(SCREEN, YELLOW, (x, y), 8)
        pygame.draw.polygon(SCREEN, BLACK, [(x, y), (x + 10, y - 5), (x + 10, y + 5)])


def draw_player():
    global mouth_timer, mouth_open

    mouth_timer += 1
    if mouth_timer > 8:
        mouth_open = not mouth_open
        mouth_timer = 0

    center = (round(player_pos.x), round(player_pos.y))

    angle = 0
    if facing_direction.x < 0:
        angle = 180
    elif facing_direction.y < 0:
        angle = 90
    elif facing_direction.y > 0:
        angle = 270

    pygame.draw.circle(SCREEN, YELLOW, center, player_radius)

    if mouth_open:
        mouth_size = 38
        angle1 = math.radians(angle - mouth_size)
        angle2 = math.radians(angle + mouth_size)

        p1 = center
        p2 = (
            center[0] + math.cos(angle1) * player_radius * 1.5,
            center[1] - math.sin(angle1) * player_radius * 1.5,
        )
        p3 = (
            center[0] + math.cos(angle2) * player_radius * 1.5,
            center[1] - math.sin(angle2) * player_radius * 1.5,
        )
        pygame.draw.polygon(SCREEN, BLACK, [p1, p2, p3])


def draw_death_animation():
    progress = min(1.0, death_timer / DEATH_DURATION)
    center = (round(player_pos.x), round(player_pos.y))
    radius = max(2, int(player_radius * (1.0 - progress * 0.65)))
    mouth_size = 25 + progress * 155

    pygame.draw.circle(SCREEN, YELLOW, center, radius)

    angle = 0
    if facing_direction.x < 0:
        angle = 180
    elif facing_direction.y < 0:
        angle = 90
    elif facing_direction.y > 0:
        angle = 270

    angle1 = math.radians(angle - mouth_size)
    angle2 = math.radians(angle + mouth_size)
    p2 = (
        center[0] + math.cos(angle1) * player_radius * 1.8,
        center[1] - math.sin(angle1) * player_radius * 1.8,
    )
    p3 = (
        center[0] + math.cos(angle2) * player_radius * 1.8,
        center[1] - math.sin(angle2) * player_radius * 1.8,
    )
    pygame.draw.polygon(SCREEN, BLACK, [center, p2, p3])

    spark_count = 8
    spark_length = int(8 + progress * 15)
    for i in range(spark_count):
        spark_angle = (math.tau / spark_count) * i + progress * 3
        inner = (
            center[0] + math.cos(spark_angle) * (player_radius + 2),
            center[1] + math.sin(spark_angle) * (player_radius + 2),
        )
        outer = (
            center[0] + math.cos(spark_angle) * (player_radius + spark_length),
            center[1] + math.sin(spark_angle) * (player_radius + spark_length),
        )
        pygame.draw.line(SCREEN, YELLOW, inner, outer, 2)


def draw_center_message(title, subtitle=None, color=WHITE, border_color=BLUE):
    panel = pygame.Rect(76, HEIGHT // 2 - 72, WIDTH - 152, 110)
    pygame.draw.rect(SCREEN, BLACK, panel)
    pygame.draw.rect(SCREEN, border_color, panel, 4)

    title_text = TITLE_FONT.render(title, False, color)
    SCREEN.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 2 - 42))

    if subtitle:
        sub_text = SMALL_FONT.render(subtitle, False, WHITE)
        SCREEN.blit(sub_text, (WIDTH // 2 - sub_text.get_width() // 2, HEIGHT // 2 - 7))


def draw_countdown_message():
    if game_state != "countdown":
        return

    remaining = math.ceil(countdown_timer / FPS)
    title = "READY!" if remaining <= 0 else str(remaining)
    draw_center_message(title, "GET READY", YELLOW, BLUE)


def draw_ghosts():
    for ghost in ghosts:
        center = (round(ghost["pos"].x), round(ghost["pos"].y + 2))

        if ghost["eaten"]:
            draw_ghost_eyes(center)
        elif is_frightened() and ghost["active"]:
            flashing = frightened_timer < 2 * FPS and (frightened_timer // 10) % 2 == 0
            draw_ghost(center, WHITE if flashing else FRIGHTENED_BLUE)
        else:
            draw_ghost(center, ghost["color"])

        label_color = WHITE if ghost["active"] else HUD_TEXT
        label_text = ghost["name"] if ghost["active"] else f"{ghost['name']} {ghost['release_at']}"
        label = SMALL_FONT.render(label_text, False, label_color)
        label_x = center[0] - label.get_width() // 2
        label_y = center[1] - 31
        pygame.draw.rect(
            SCREEN,
            BLACK,
            (label_x - 2, label_y - 1, label.get_width() + 4, label.get_height() + 1),
        )
        SCREEN.blit(label, (label_x, label_y))


def update_ghost(ghost):
    if not ghost["active"] and not ghost["eaten"]:
        return

    if ghost["progress"] < 1.0:
        speed = ghost["speed"]
        if ghost["eaten"]:
            speed *= 1.8
        elif is_frightened():
            speed *= 0.7

        ghost["progress"] = min(1.0, ghost["progress"] + speed)
        ghost["pos"] = ghost["start_pos"].lerp(ghost["target_pos"], ghost["progress"])

        if ghost["progress"] >= 1.0:
            ghost["tile"] = ghost["target_tile"]
            ghost["pos"] = tile_center(ghost["tile"])
            ghost["wrapping"] = False

            if ghost["eaten"] and ghost["tile"] == ghost["initial_tile"]:
                ghost["eaten"] = False
                ghost["active"] = pellets_eaten >= ghost["release_at"]

        return

    if ghost["eaten"]:
        path = find_path_dijkstra(ghost["tile"], ghost["initial_tile"])
        if len(path) < 2:
            return
        next_target = path[1]
    elif is_frightened():
        next_target = frightened_ghost_target(ghost)
    else:
        path = find_ghost_path(ghost, player_tile)
        if len(path) < 2:
            return
        next_target = path[1]

    ghost["target_tile"] = next_target
    ghost["start_pos"] = tile_center(ghost["tile"])
    step_direction = wrapped_step_direction(ghost["tile"], ghost["target_tile"])
    ghost["wrapping"] = is_wrap_move(ghost["tile"], step_direction)

    if ghost["wrapping"]:
        ghost["target_pos"] = offscreen_target(ghost["tile"], step_direction)
    else:
        ghost["target_pos"] = tile_center(ghost["target_tile"])

    ghost["progress"] = 0.0


def update_ghosts():
    global frightened_timer

    if frightened_timer > 0:
        frightened_timer -= 1

    for ghost in ghosts:
        update_ghost(ghost)


def start_step(move_direction):
    global direction, facing_direction, start_pos, target_pos, target_tile, step_progress
    global wrapping_step

    candidate = next_tile(player_tile, move_direction)
    wrapped_candidate = wrap_tile(candidate)
    should_wrap = is_wrap_move(player_tile, move_direction)

    if not is_walkable(wrapped_candidate):
        return False

    direction = move_direction.copy()
    facing_direction = move_direction.copy()
    target_tile = wrapped_candidate
    wrapping_step = should_wrap
    start_pos = tile_center(player_tile)

    if wrapping_step:
        target_pos = offscreen_target(player_tile, move_direction)
    else:
        target_pos = tile_center(target_tile)

    step_progress = 0.0
    return True


def update_player():
    global player_tile, player_pos, step_progress, direction, wrapping_step

    if step_progress >= 1.0:
        if queued_direction.length_squared() > 0 and start_step(queued_direction):
            return

        if direction.length_squared() > 0 and start_step(direction):
            return

        direction = pygame.Vector2(0, 0)
        player_pos = tile_center(player_tile)
        return

    step_progress = min(1.0, step_progress + step_speed)
    player_pos = start_pos.lerp(target_pos, step_progress)

    if step_progress >= 1.0:
        player_tile = target_tile
        player_pos = tile_center(player_tile)
        wrapping_step = False


def eat_pellets():
    global score, pellets_eaten, frightened_timer, ghost_eat_score

    if player_tile in pellets:
        pellets.remove(player_tile)
        score += 10
        pellets_eaten += 1
        release_ghosts()

    if player_tile in power_pellets:
        power_pellets.remove(player_tile)
        score += 50
        pellets_eaten += 1
        frightened_timer = FRIGHTENED_DURATION
        ghost_eat_score = 200
        release_ghosts()


def check_ghost_collision():
    global lives, game_state, death_timer, direction, queued_direction, score, ghost_eat_score

    for ghost in ghosts:
        if not ghost["active"] and not ghost["eaten"]:
            continue

        distance = player_pos.distance_to(ghost["pos"])
        if distance < player_radius + 9:
            if is_frightened() and not ghost["eaten"]:
                score += ghost_eat_score
                ghost_eat_score *= 2
                ghost["eaten"] = True
                ghost["active"] = True
                ghost["progress"] = 1.0
                return

            if ghost["eaten"]:
                continue

            lives -= 1
            game_state = "dying"
            death_timer = 0
            direction = pygame.Vector2(0, 0)
            queued_direction = pygame.Vector2(0, 0)

            return


def draw_win_message():
    if remaining_food() > 0:
        return

    overlay = pygame.Surface((WIDTH, MAZE_HEIGHT))
    overlay.set_alpha(190)
    overlay.fill(BLACK)
    SCREEN.blit(overlay, (0, 0))

    panel = pygame.Rect(34, HEIGHT // 2 - 70, WIDTH - 68, 110)
    pygame.draw.rect(SCREEN, BLACK, panel)
    pygame.draw.rect(SCREEN, BLUE, panel, 4)

    text = FONT.render("YOU CLEARED THE MAP!", False, YELLOW)
    sub = SMALL_FONT.render("R RESTART   ESC QUIT", False, WHITE)

    SCREEN.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 42))
    SCREEN.blit(sub, (WIDTH // 2 - sub.get_width() // 2, HEIGHT // 2 - 6))


def draw_game_over_message():
    if not game_over:
        return

    overlay = pygame.Surface((WIDTH, MAZE_HEIGHT))
    overlay.set_alpha(205)
    overlay.fill(BLACK)
    SCREEN.blit(overlay, (0, 0))

    panel = pygame.Rect(46, HEIGHT // 2 - 70, WIDTH - 92, 110)
    pygame.draw.rect(SCREEN, BLACK, panel)
    pygame.draw.rect(SCREEN, RED, panel, 4)

    text = FONT.render("GAME OVER", False, RED)
    sub = SMALL_FONT.render("R RESTART   ESC QUIT", False, WHITE)

    SCREEN.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 42))
    SCREEN.blit(sub, (WIDTH // 2 - sub.get_width() // 2, HEIGHT // 2 - 6))


# =========================
# MAIN LOOP
# =========================
running = True

while running:
    CLOCK.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_r and (game_over or remaining_food() == 0):
                restart_game()
            elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                queued_direction = DIRECTIONS["right"].copy()
            elif event.key in [pygame.K_LEFT, pygame.K_a]:
                queued_direction = DIRECTIONS["left"].copy()
            elif event.key in [pygame.K_UP, pygame.K_w]:
                queued_direction = DIRECTIONS["up"].copy()
            elif event.key in [pygame.K_DOWN, pygame.K_s]:
                queued_direction = DIRECTIONS["down"].copy()

    if game_state == "countdown" and remaining_food() > 0 and not game_over:
        update_countdown()
    elif game_state == "dying":
        update_death_animation()
    elif game_state == "playing" and remaining_food() > 0 and not game_over:
        update_player()
        update_ghosts()
        eat_pellets()
        check_ghost_collision()

    draw_background()
    draw_pellets()
    draw_walls()
    draw_ghost_cage()
    draw_ghosts()
    if game_state == "dying":
        draw_death_animation()
    else:
        draw_player()
    draw_hud()
    draw_countdown_message()
    draw_win_message()
    draw_game_over_message()

    pygame.display.flip()

pygame.quit()
sys.exit()
