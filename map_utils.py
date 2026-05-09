from config import RAW_MAP, ROWS, COLS


def parse_map():
    """Parse RAW_MAP into game objects and starting positions."""
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
                pellets.discard(pos)  # starting tile is not a pellet
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
    """Return all walkable neighbors of pos in a consistent order."""
    x, y = pos
    candidates = [
        (x + 1, y),  # right
        (x, y + 1),  # down
        (x - 1, y),  # left
        (x, y - 1),  # up
    ]
    return [p for p in candidates if is_walkable(p, walls)]


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
