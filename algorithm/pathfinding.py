"""
Pathfinding algorithms for ghosts (A*, BFS, Dijkstra)
"""

import heapq
from collections import deque
from map import ghost_neighbors
from config import COLS, ROWS


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
    """Find path using Dijkstra's algorithm"""
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
    """Find path using Breadth-First Search"""
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


def find_path_dfs(start, goal):
    """Find path using Depth-First Search"""
    stack = [start]
    came_from = {}
    visited = {start}

    while stack:
        current = stack.pop()

        if current == goal:
            return reconstruct_path(came_from, start, goal)

        for neighbor in ghost_neighbors(current):
            if neighbor not in visited:
                visited.add(neighbor)
                came_from[neighbor] = current
                stack.append(neighbor)

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
