import heapq
from map_utils import get_neighbors, reconstruct_path, manhattan_distance


def astar_path(start, goal, walls):
    """
    A* Search — combines Dijkstra's cost-so-far (g) with a heuristic (h).
    Uses Manhattan distance as h, which is admissible on a 4-directional grid.
    Typically faster than BFS/Dijkstra because it's guided toward the goal.

    To swap in a different heuristic, replace manhattan_distance with your own
    function that accepts (pos, goal) and returns a non-negative estimate.
    """
    if start == goal:
        return []

    open_set = [(0, start)]
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

    return []  # no path found
