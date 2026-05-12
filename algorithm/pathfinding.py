"""
Pathfinding algorithms for ghosts (A*, BFS, Dijkstra)
"""

import heapq
from collections import deque
from map import ghost_neighbors
from config import COLS, ROWS
import time
from algorithm.analysis import global_metrics


def grid_distance(first, second):
    """Calculate grid distance considering map wrapping"""
    dx = abs(first[0] - second[0])
    dy = abs(first[1] - second[1])
    return min(dx, COLS - dx) + min(dy, ROWS - dy)


def reconstruct_path(came_from, start, goal):
    """Reconstruct path from came_from mapping"""
    if goal not in came_from and goal != start:
        return []

    path = [goal]
    current = goal
    while current != start:
        current = came_from[current]
        path.append(current)

    path.reverse()
    return path


def find_path_astar(start, goal):
    """Find path using A* algorithm"""
    t0 = time.perf_counter()
    frontier = []
    heapq.heappush(frontier, (0, start))
    came_from = {}
    cost_so_far = {start: 0}
    nodes_explored = 0

    while frontier:
        _, current = heapq.heappop(frontier)
        nodes_explored += 1
        if current == goal:
            path = reconstruct_path(came_from, start, goal)
            global_metrics.record_search(
                "astar",
                (time.perf_counter() - t0) * 1000,
                len(path),
                nodes_explored,
                True,
            )
            return path

        for neighbor in ghost_neighbors(current):
            new_cost = cost_so_far[current] + 1
            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = new_cost
                priority = new_cost + grid_distance(neighbor, goal)
                heapq.heappush(frontier, (priority, neighbor))
                came_from[neighbor] = current

    global_metrics.record_search(
        "astar", (time.perf_counter() - t0) * 1000, 0, nodes_explored, False
    )
    return []


def find_path_dijkstra(start, goal):
    """Find path using Dijkstra's algorithm"""
    t0 = time.perf_counter()
    frontier = []
    heapq.heappush(frontier, (0, start))
    came_from = {}
    cost_so_far = {start: 0}
    nodes_explored = 0

    while frontier:
        current_cost, current = heapq.heappop(frontier)
        nodes_explored += 1

        if current == goal:
            path = reconstruct_path(came_from, start, goal)
            global_metrics.record_search(
                "dijkstra",
                (time.perf_counter() - t0) * 1000,
                len(path),
                nodes_explored,
                True,
            )
            return path

        if current_cost > cost_so_far[current]:
            continue

        for neighbor in ghost_neighbors(current):
            new_cost = current_cost + 1
            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = new_cost
                heapq.heappush(frontier, (new_cost, neighbor))
                came_from[neighbor] = current

    global_metrics.record_search(
        "dijkstra", (time.perf_counter() - t0) * 1000, 0, nodes_explored, False
    )
    return []


def find_path_bfs(start, goal):
    """Find path using Breadth-First Search"""
    t0 = time.perf_counter()
    queue = deque([start])
    came_from = {}
    visited = {start}
    nodes_explored = 0

    while queue:
        current = queue.popleft()
        nodes_explored += 1
        if current == goal:
            path = reconstruct_path(came_from, start, goal)
            global_metrics.record_search(
                "bfs",
                (time.perf_counter() - t0) * 1000,
                len(path),
                nodes_explored,
                True,
            )
            return path

        for neighbor in ghost_neighbors(current):
            if neighbor not in visited:
                visited.add(neighbor)
                came_from[neighbor] = current
                queue.append(neighbor)

    global_metrics.record_search(
        "bfs", (time.perf_counter() - t0) * 1000, 0, nodes_explored, False
    )
    return []


def find_path_dfs(start, goal):
    """Find path using Depth-First Search"""
    t0 = time.perf_counter()
    stack = [start]
    came_from = {}
    visited = {start}
    nodes_explored = 0

    while stack:
        current = stack.pop()
        nodes_explored += 1

        if current == goal:
            path = reconstruct_path(came_from, start, goal)
            global_metrics.record_search(
                "dfs",
                (time.perf_counter() - t0) * 1000,
                len(path),
                nodes_explored,
                True,
            )
            return path

        for neighbor in ghost_neighbors(current):
            if neighbor not in visited:
                visited.add(neighbor)
                came_from[neighbor] = current
                stack.append(neighbor)

    global_metrics.record_search(
        "dfs", (time.perf_counter() - t0) * 1000, 0, nodes_explored, False
    )
    return []


def find_path(ghost, goal):
    """Route to the appropriate pathfinding algorithm based on ghost type"""
    algorithm = ghost["algorithm"]

    if algorithm == "astar":
        return find_path_astar(ghost["tile"], goal)
    elif algorithm == "bfs":
        return find_path_bfs(ghost["tile"], goal)
    elif algorithm == "dfs":
        return find_path_dfs(ghost["tile"], goal)
    else:  # dijkstra
        return find_path_dijkstra(ghost["tile"], goal)
