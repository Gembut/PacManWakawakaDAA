import pygame
import sys
import heapq
from collections import deque

# =========================
# KONFIGURASI DASAR GAME
# =========================

pygame.init()

TILE_SIZE = 28
ROWS = 21
COLS = 21

WIDTH = COLS * TILE_SIZE
HEIGHT = ROWS * TILE_SIZE + 70

FPS = 12
GHOST_MOVE_DELAY = 3  # Semakin besar, ghost semakin lambat

SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pacman AI DAA - A*, BFS, Dijkstra")

CLOCK = pygame.time.Clock()

# Warna
BLACK = (0, 0, 0)
NAVY = (10, 10, 35)
BLUE_WALL = (30, 70, 200)
YELLOW = (255, 230, 40)
WHITE = (255, 255, 255)
GREEN = (50, 220, 90)
RED = (230, 60, 60)
CYAN = (40, 200, 255)
PURPLE = (180, 80, 255)

FONT = pygame.font.SysFont("arial", 18)
BIG_FONT = pygame.font.SysFont("arial", 40, bold=True)

# =========================
# MAP GAME
# # = Wall
# . = Pellet
# P = Pacman
# A = Ghost A*
# B = Ghost BFS
# D = Ghost Dijkstra
# =========================

RAW_MAP = [
    "#####################",
    "#P........#.........#",
    "#.###.###.#.###.###.#",
    "#...................#",
    "#.###.#.#####.#.###.#",
    "#.....#...#...#.....#",
    "#####.###.#.###.#####",
    "#.........A.........#",
    "#.###.###...###.###.#",
    "#...#.....#.....#...#",
    "###.#.###.#.###.#.###",
    "#.....#...B...#.....#",
    "#.###.#.#####.#.###.#",
    "#...................#",
    "#.###.###.#.###.###.#",
    "#.........D.........#",
    "#####.#.#####.#.#####",
    "#.....#...#...#.....#",
    "#.#######.#.#######.#",
    "#...................#",
    "#####################",
]

# =========================
# FUNGSI UTILITAS MAP
# =========================

def parse_map():
    walls = set()
    pellets = set()
    pacman_pos = None
    ghost_positions = {}

    for y, row in enumerate(RAW_MAP):
        for x, char in enumerate(row):
            pos = (x, y)

            if char == "#":
                walls.add(pos)
            elif char == ".":
                pellets.add(pos)
            elif char == "P":
                pacman_pos = pos
            elif char == "A":
                ghost_positions["astar"] = pos
            elif char == "B":
                ghost_positions["bfs"] = pos
            elif char == "D":
                ghost_positions["dijkstra"] = pos

    return walls, pellets, pacman_pos, ghost_positions


def is_walkable(pos, walls):
    x, y = pos
    return 0 <= x < COLS and 0 <= y < ROWS and pos not in walls


def get_neighbors(pos, walls):
    x, y = pos

    # Urutan neighbor dibuat konsisten agar hasil algoritma stabil
    possible_moves = [
        (x + 1, y),  # kanan
        (x, y + 1),  # bawah
        (x - 1, y),  # kiri
        (x, y - 1),  # atas
    ]

    neighbors = []

    for move in possible_moves:
        if is_walkable(move, walls):
            neighbors.append(move)

    return neighbors


def manhattan_distance(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def reconstruct_path(parent, start, goal):
    if goal not in parent and goal != start:
        return []

    path = []
    current = goal

    while current != start:
        path.append(current)
        current = parent[current]

    path.reverse()
    return path


# =========================
# ALGORITMA BFS
# =========================

def bfs_path(start, goal, walls):
    queue = deque([start])
    visited = {start}
    parent = {}

    while queue:
        current = queue.popleft()

        if current == goal:
            return reconstruct_path(parent, start, goal)

        for neighbor in get_neighbors(current, walls):
            if neighbor not in visited:
                visited.add(neighbor)
                parent[neighbor] = current
                queue.append(neighbor)

    return []


# =========================
# ALGORITMA DIJKSTRA
# =========================

def dijkstra_path(start, goal, walls):
    priority_queue = []
    heapq.heappush(priority_queue, (0, start))

    distances = {start: 0}
    parent = {}
    visited = set()

    while priority_queue:
        current_distance, current = heapq.heappop(priority_queue)

        if current in visited:
            continue

        visited.add(current)

        if current == goal:
            return reconstruct_path(parent, start, goal)

        for neighbor in get_neighbors(current, walls):
            weight = 1
            new_distance = current_distance + weight

            if neighbor not in distances or new_distance < distances[neighbor]:
                distances[neighbor] = new_distance
                parent[neighbor] = current
                heapq.heappush(priority_queue, (new_distance, neighbor))

    return []


# =========================
# ALGORITMA A*
# =========================

def astar_path(start, goal, walls):
    open_set = []
    heapq.heappush(open_set, (0, start))

    parent = {}
    g_score = {start: 0}
    visited = set()

    while open_set:
        _, current = heapq.heappop(open_set)

        if current in visited:
            continue

        visited.add(current)

        if current == goal:
            return reconstruct_path(parent, start, goal)

        for neighbor in get_neighbors(current, walls):
            tentative_g = g_score[current] + 1

            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                parent[neighbor] = current
                g_score[neighbor] = tentative_g

                f_score = tentative_g + manhattan_distance(neighbor, goal)
                heapq.heappush(open_set, (f_score, neighbor))

    return []


# =========================
# CLASS PACMAN
# =========================

class Pacman:
    def __init__(self, position):
        self.position = position
        self.direction = (0, 0)
        self.next_direction = (0, 0)

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.next_direction = (0, -1)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.next_direction = (0, 1)
            elif event.key in (pygame.K_LEFT, pygame.K_a):
                self.next_direction = (-1, 0)
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.next_direction = (1, 0)

    def update(self, walls):
        x, y = self.position

        # Coba ganti arah terlebih dahulu
        next_pos = (x + self.next_direction[0], y + self.next_direction[1])

        if is_walkable(next_pos, walls):
            self.direction = self.next_direction

        # Bergerak sesuai arah saat ini
        move_pos = (x + self.direction[0], y + self.direction[1])

        if is_walkable(move_pos, walls):
            self.position = move_pos

    def draw(self, screen):
        center_x = self.position[0] * TILE_SIZE + TILE_SIZE // 2
        center_y = self.position[1] * TILE_SIZE + TILE_SIZE // 2

        pygame.draw.circle(
            screen,
            YELLOW,
            (center_x, center_y),
            TILE_SIZE // 2 - 3
        )


# =========================
# CLASS GHOST
# =========================

class Ghost:
    def __init__(self, position, algorithm, color, label):
        self.position = position
        self.algorithm = algorithm
        self.color = color
        self.label = label
        self.path = []

    def find_path(self, target, walls):
        if self.algorithm == "astar":
            self.path = astar_path(self.position, target, walls)
        elif self.algorithm == "bfs":
            self.path = bfs_path(self.position, target, walls)
        elif self.algorithm == "dijkstra":
            self.path = dijkstra_path(self.position, target, walls)

    def update(self, target, walls):
        self.find_path(target, walls)

        if self.path:
            self.position = self.path[0]

    def draw(self, screen):
        x = self.position[0] * TILE_SIZE
        y = self.position[1] * TILE_SIZE

        ghost_rect = pygame.Rect(
            x + 4,
            y + 4,
            TILE_SIZE - 8,
            TILE_SIZE - 8
        )

        pygame.draw.rect(screen, self.color, ghost_rect, border_radius=8)

        # Mata
        pygame.draw.circle(screen, WHITE, (x + 10, y + 11), 4)
        pygame.draw.circle(screen, WHITE, (x + 18, y + 11), 4)
        pygame.draw.circle(screen, BLACK, (x + 10, y + 11), 2)
        pygame.draw.circle(screen, BLACK, (x + 18, y + 11), 2)

        # Label algoritma
        text = FONT.render(self.label, True, WHITE)
        screen.blit(text, (x - 2, y - 18))

    def draw_path_preview(self, screen):
        # Menampilkan sedikit path agar algoritma terlihat
        for pos in self.path[:8]:
            center_x = pos[0] * TILE_SIZE + TILE_SIZE // 2
            center_y = pos[1] * TILE_SIZE + TILE_SIZE // 2

            pygame.draw.circle(
                screen,
                self.color,
                (center_x, center_y),
                4
            )


# =========================
# DRAWING FUNCTIONS
# =========================

def draw_map(screen, walls, pellets):
    screen.fill(BLACK)

    for y in range(ROWS):
        for x in range(COLS):
            pos = (x, y)
            rect = pygame.Rect(
                x * TILE_SIZE,
                y * TILE_SIZE,
                TILE_SIZE,
                TILE_SIZE
            )

            if pos in walls:
                pygame.draw.rect(screen, BLUE_WALL, rect)
                pygame.draw.rect(screen, NAVY, rect, 2)
            else:
                pygame.draw.rect(screen, BLACK, rect)

    for pellet in pellets:
        center_x = pellet[0] * TILE_SIZE + TILE_SIZE // 2
        center_y = pellet[1] * TILE_SIZE + TILE_SIZE // 2

        pygame.draw.circle(screen, WHITE, (center_x, center_y), 3)


def draw_ui(screen, score, pellets_left, game_state):
    ui_y = ROWS * TILE_SIZE

    pygame.draw.rect(screen, NAVY, (0, ui_y, WIDTH, 70))

    score_text = FONT.render(f"Score: {score}", True, WHITE)
    pellets_text = FONT.render(f"Pellets Left: {pellets_left}", True, WHITE)
    info_text = FONT.render(
        "Ghost AI: Red=A* | Cyan=BFS | Purple=Dijkstra | Move: WASD / Arrow Keys | R=Restart",
        True,
        WHITE
    )

    screen.blit(score_text, (20, ui_y + 10))
    screen.blit(pellets_text, (150, ui_y + 10))
    screen.blit(info_text, (20, ui_y + 38))

    if game_state == "game_over":
        overlay = pygame.Surface((WIDTH, ROWS * TILE_SIZE))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))

        text = BIG_FONT.render("GAME OVER", True, RED)
        restart = FONT.render("Press R to Restart", True, WHITE)

        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 80))
        screen.blit(restart, (WIDTH // 2 - restart.get_width() // 2, HEIGHT // 2 - 30))

    elif game_state == "win":
        overlay = pygame.Surface((WIDTH, ROWS * TILE_SIZE))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))

        text = BIG_FONT.render("YOU WIN!", True, GREEN)
        restart = FONT.render("Press R to Restart", True, WHITE)

        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 80))
        screen.blit(restart, (WIDTH // 2 - restart.get_width() // 2, HEIGHT // 2 - 30))


# =========================
# GAME RESET
# =========================

def create_game():
    walls, pellets, pacman_start, ghost_starts = parse_map()

    pacman = Pacman(pacman_start)

    ghosts = [
        Ghost(ghost_starts["astar"], "astar", RED, "A*"),
        Ghost(ghost_starts["bfs"], "bfs", CYAN, "BFS"),
        Ghost(ghost_starts["dijkstra"], "dijkstra", PURPLE, "DIJ"),
    ]

    score = 0
    game_state = "playing"

    return walls, pellets, pacman, ghosts, score, game_state


# =========================
# MAIN LOOP
# =========================

def main():
    walls, pellets, pacman, ghosts, score, game_state = create_game()
    ghost_move_counter = 0

    while True:
        CLOCK.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            pacman.handle_input(event)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    walls, pellets, pacman, ghosts, score, game_state = create_game()
                    ghost_move_counter = 0

        if game_state == "playing":
            pacman.update(walls)

            # Pacman makan pellet
            if pacman.position in pellets:
                pellets.remove(pacman.position)
                score += 10

            # Ghost dibuat lebih lambat dari Pacman
            ghost_move_counter += 1

            if ghost_move_counter >= GHOST_MOVE_DELAY:
                for ghost in ghosts:
                    ghost.update(pacman.position, walls)

                ghost_move_counter = 0

            # Cek collision dengan ghost
            for ghost in ghosts:
                if ghost.position == pacman.position:
                    game_state = "game_over"

            # Cek menang
            if len(pellets) == 0:
                game_state = "win"

        draw_map(SCREEN, walls, pellets)

        # Preview path hantu
        for ghost in ghosts:
            ghost.draw_path_preview(SCREEN)

        pacman.draw(SCREEN)

        for ghost in ghosts:
            ghost.draw(SCREEN)

        draw_ui(SCREEN, score, len(pellets), game_state)

        pygame.display.flip()


if __name__ == "__main__":
    main()