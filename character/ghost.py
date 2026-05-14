"""
Ghost logic and behavior
"""

from config import GHOSTS_CONFIG, TILE_SIZE, FPS
from map import GHOST_EXIT_TILES, tile_center, ghost_neighbors, is_ghost_walkable
from algorithm.pathfinding import grid_distance


def create_ghost(config):
    """Create a ghost object from configuration"""
    initial_tile = config["initial_tile"]
    return {
        "name": config["name"],
        "algorithm": config["algorithm"],
        "color": config["color"],
        "initial_tile": initial_tile,
        "tile": initial_tile,
        "target_tile": initial_tile,
        "pos": tile_center(initial_tile),
        "start_pos": tile_center(initial_tile),
        "target_pos": tile_center(initial_tile),
        "progress": 1.0,
        "speed": config["speed"],
        "wrapping": False,
        "release_at": config["release_at"],
        "active": config["release_at"] == 0,
        "eaten": False,
        "ignore_frightened": False,
        "waiting_for_power_end": False,
    }


def create_all_ghosts():
    """Create all ghost objects from config"""
    return [create_ghost(config) for config in GHOSTS_CONFIG]


def reset_ghost_position(ghost, active=False):
    """Reset ghost to initial position"""
    ghost["tile"] = ghost["initial_tile"]
    ghost["target_tile"] = ghost["initial_tile"]
    ghost["pos"] = tile_center(ghost["initial_tile"])
    ghost["start_pos"] = ghost["pos"].copy()
    ghost["target_pos"] = ghost["pos"].copy()
    ghost["progress"] = 1.0
    ghost["wrapping"] = False
    ghost["active"] = active
    ghost["eaten"] = False
    ghost["ignore_frightened"] = False
    ghost["waiting_for_power_end"] = False


def frightened_ghost_target(ghost, player_tile):
    """Get target for frightened ghost (flee from player)"""
    choices = ghost_neighbors(ghost["tile"])
    if not choices:
        return ghost["tile"]

    return max(choices, key=lambda tile: grid_distance(tile, player_tile))


def ghost_exit_is_busy(ghosts):
    """Check whether an active ghost is still occupying the cage exit path."""
    for ghost in ghosts:
        if not ghost["active"] and not ghost["eaten"]:
            continue

        if ghost["tile"] in GHOST_EXIT_TILES or ghost["target_tile"] in GHOST_EXIT_TILES:
            return True

    return False


def release_ghosts(ghosts, pellets_eaten):
    """Release the next eligible ghost based on pellets eaten."""
    if ghost_exit_is_busy(ghosts):
        return None

    locked_ghosts = [
        ghost
        for ghost in ghosts
        if not ghost["active"]
        and not ghost["eaten"]
        and not ghost.get("waiting_for_power_end")
    ]
    locked_ghosts.sort(key=lambda ghost: ghost["release_at"])

    for ghost in locked_ghosts:
        if pellets_eaten >= ghost["release_at"]:
            ghost["active"] = True
            return ghost

    return None


def update_ghost(ghost, player_tile, is_frightened, pathfinding_func):
    """Update a single ghost's position and behavior"""
    from map import wrapped_step_direction, is_wrap_move, offscreen_target

    if not ghost["active"] and not ghost["eaten"]:
        return

    ghost_is_frightened = (
        is_frightened and not ghost["eaten"] and not ghost.get("ignore_frightened")
    )

    # Update position if still moving
    if ghost["progress"] < 1.0:
        speed = ghost["speed"]
        if ghost["eaten"]:
            speed *= 1.8
        elif ghost_is_frightened:
            speed *= 0.7

        ghost["progress"] = min(1.0, ghost["progress"] + speed)
        ghost["pos"] = ghost["start_pos"].lerp(ghost["target_pos"], ghost["progress"])

        if ghost["progress"] >= 1.0:
            ghost["tile"] = ghost["target_tile"]
            ghost["pos"] = tile_center(ghost["tile"])
            ghost["wrapping"] = False

            if ghost["eaten"] and ghost["tile"] == ghost["initial_tile"]:
                ghost["eaten"] = False
                if is_frightened:
                    ghost["active"] = False
                    ghost["waiting_for_power_end"] = True
                else:
                    ghost["active"] = True

        return

    # Calculate next move
    if ghost["eaten"]:
        # Eaten ghost returns to cage
        path = pathfinding_func(ghost, ghost["initial_tile"])
        if len(path) < 2:
            return
        next_target = path[1]
    elif ghost_is_frightened:
        # Frightened ghost flees
        next_target = frightened_ghost_target(ghost, player_tile)
    else:
        # Normal ghost chases player
        path = pathfinding_func(ghost, player_tile)
        if len(path) < 2:
            return
        next_target = path[1]

    # Prepare for next step
    ghost["target_tile"] = next_target
    ghost["start_pos"] = tile_center(ghost["tile"])
    step_direction = wrapped_step_direction(ghost["tile"], ghost["target_tile"])
    ghost["wrapping"] = is_wrap_move(ghost["tile"], step_direction)

    if ghost["wrapping"]:
        ghost["target_pos"] = offscreen_target(ghost["tile"], step_direction)
    else:
        ghost["target_pos"] = tile_center(ghost["target_tile"])

    ghost["progress"] = 0.0
