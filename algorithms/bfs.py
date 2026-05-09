from collections import deque
from map_utils import get_neighbors, reconstruct_path


def bfs_path(start, goal, walls):
    """
    Breadth-First Search — finds the shortest path in terms of number of steps.
    Explores all nodes level by level; no heuristic, no edge weights.
    """
    if start == goal:
        return []

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

    return []  # no path found
