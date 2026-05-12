"""
Game state management
"""

from config import FPS, FRIGHTENED_DURATION
from map import parse_game_map, GAME_MAP
from character.player import PlayerState
from character.ghost import create_all_ghosts, reset_ghost_position, release_ghosts


class GameState:
    """Central game state manager"""

    def __init__(self):
        # Parse map
        walls, pellets, power_pellets, player_start_tile = parse_game_map(GAME_MAP)

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
        self.countdown_timer = 3 * FPS
        self.death_timer = 0
        self.death_duration = 90
        self.frightened_timer = 0
        self.ghost_eat_score = 200

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
        self.countdown_timer = 3 * FPS
        self.frightened_timer = 0
        self.ghost_eat_score = 200

        for ghost in self.ghosts:
            reset_ghost_position(ghost)

    def restart_game(self):
        """Restart the entire game"""
        self.pellets = self.initial_pellets.copy()
        self.power_pellets = self.initial_power_pellets.copy()

        self.player = PlayerState(self.player_start_tile)
        self.player.score = 0
        self.player.lives = 3
        self.player.pellets_eaten = 0

        self.game_state = "countdown"
        self.game_over = False
        self.countdown_timer = 3 * FPS
        self.death_timer = 0
        self.frightened_timer = 0
        self.ghost_eat_score = 200

        self.ghosts = create_all_ghosts()
        self.reset_round()

    def start_countdown(self):
        """Start countdown before game starts"""
        self.game_state = "countdown"
        self.countdown_timer = 3 * FPS

    def handle_death(self):
        """Handle player death"""
        self.player.lives -= 1
        if self.player.lives <= 0:
            self.game_over = True
            self.game_state = "game_over"
        else:
            self.reset_round()
            release_ghosts(self.ghosts, self.player.pellets_eaten)
            self.start_countdown()

    def activate_power_mode(self):
        """Activate frightened/power mode"""
        self.frightened_timer = FRIGHTENED_DURATION
        self.ghost_eat_score = 200
