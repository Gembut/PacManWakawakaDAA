"""
Game state management
"""

import random

from config import FPS, COUNTDOWN_SECONDS, FRIGHTENED_DURATION, GHOST_RELEASE_DELAY
from map import GAME_MAPS, parse_game_map, set_active_map
from character.player import PlayerState
from character.ghost import create_all_ghosts, reset_ghost_position, release_ghosts


class GameState:
    """Central game state manager"""

    def __init__(self, map_index=None):
        self.map_index = self.random_map_index() if map_index is None else map_index
        self.ghost_release_cooldown = 0

        # Parse map
        walls, pellets, power_pellets, player_start_tile = parse_game_map(
            set_active_map(self.map_index)
        )

        self.walls = walls
        self.initial_pellets = pellets.copy()
        self.initial_power_pellets = power_pellets.copy()
        self.pellets = pellets
        self.power_pellets = power_pellets

        # Player
        self.player = PlayerState(player_start_tile)
        self.player_start_tile = player_start_tile

        # Ghosts
        self.ghosts = create_all_ghosts()

        # Game state
        self.game_state = "countdown"
        self.game_over = False
        self.countdown_timer = COUNTDOWN_SECONDS * FPS
        self.death_timer = 0
        self.death_duration = 90
        self.frightened_timer = 0
        self.ghost_eat_score = 200
        self.elapsed_frames = 0

        # Animation
        self.mouth_timer = 0
        self.mouth_open = True

    def remaining_food(self):
        """Count remaining pellets"""
        return len(self.pellets) + len(self.power_pellets)

    def is_frightened(self):
        """Check if in frightened mode"""
        return self.frightened_timer > 0

    def reset_round(self):
        """Reset for a new round"""
        self.player.reset_position(self.player_start_tile)
        self.countdown_timer = COUNTDOWN_SECONDS * FPS
        self.frightened_timer = 0
        self.ghost_eat_score = 200
        self.ghost_release_cooldown = 0

        for ghost in self.ghosts:
            reset_ghost_position(ghost)

    def random_map_index(self):
        """Pick a random map, preferring a different one when possible."""
        if len(GAME_MAPS) <= 1:
            return 0

        current_map_index = getattr(self, "map_index", None)
        choices = [
            index for index in range(len(GAME_MAPS)) if index != current_map_index
        ]
        return random.choice(choices)

    def restart_game(self, randomize_map=True):
        """Restart the entire game"""
        if randomize_map:
            self.map_index = self.random_map_index()

        walls, pellets, power_pellets, player_start_tile = parse_game_map(
            set_active_map(self.map_index)
        )

        self.walls = walls
        self.initial_pellets = pellets.copy()
        self.initial_power_pellets = power_pellets.copy()
        self.player_start_tile = player_start_tile

        self.pellets = self.initial_pellets.copy()
        self.power_pellets = self.initial_power_pellets.copy()

        self.player = PlayerState(self.player_start_tile)
        self.player.score = 0
        self.player.lives = 3
        self.player.pellets_eaten = 0

        self.game_state = "countdown"
        self.game_over = False
        self.countdown_timer = COUNTDOWN_SECONDS * FPS
        self.death_timer = 0
        self.frightened_timer = 0
        self.ghost_eat_score = 200
        self.elapsed_frames = 0
        self.ghost_release_cooldown = 0

        self.ghosts = create_all_ghosts()
        self.reset_round()

    def next_map(self):
        """Switch to the next map and restart the game."""
        self.map_index = (self.map_index + 1) % len(GAME_MAPS)
        self.restart_game(randomize_map=False)

    def start_countdown(self):
        """Start countdown before game starts"""
        self.game_state = "countdown"
        self.countdown_timer = COUNTDOWN_SECONDS * FPS

    def handle_death(self):
        """Handle player death"""
        self.player.lives -= 1
        if self.player.lives <= 0:
            self.game_over = True
            self.game_state = "game_over"
        else:
            self.reset_round()
            self.try_release_ghost()
            self.start_countdown()

    def activate_power_mode(self):
        """Activate frightened/power mode"""
        self.frightened_timer = FRIGHTENED_DURATION
        self.ghost_eat_score = 200
        for ghost in self.ghosts:
            ghost["ignore_frightened"] = False

    def update_ghost_release_cooldown(self):
        """Advance the delay between ghost releases."""
        if self.ghost_release_cooldown > 0:
            self.ghost_release_cooldown -= 1

    def try_release_ghost(self):
        """Release at most one eligible ghost after the doorway is clear."""
        if self.ghost_release_cooldown > 0:
            return None

        released_ghost = release_ghosts(self.ghosts, self.player.pellets_eaten)
        if released_ghost is not None:
            self.ghost_release_cooldown = GHOST_RELEASE_DELAY

        return released_ghost
