import heapq
from map_utils import get_neighbors, reconstruct_path


def dijkstra_path(start, goal, walls):
    """
    Dijkstra's Algorithm — finds the lowest-cost path.
    All edges have weight 1 in this grid, so the result matches BFS,
    but the priority-queue approach generalises to weighted grids.
    """
    if start == goal:
        return []

    priority_queue = [(0, start)]
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
            weight = 1  # uniform cost; change here for weighted grids
            new_distance = current_distance + weight

            if neighbor not in distances or new_distance < distances[neighbor]:
                distances[neighbor] = new_distance
                parent[neighbor] = current
                heapq.heappush(priority_queue, (new_distance, neighbor))

    return []  # no path found
