"""
Player logic and movement
"""

import pygame
from config import TILE_SIZE, DIRECTIONS, PLAYER_RADIUS, PLAYER_SPEED
from map import (
    tile_center,
    next_tile,
    is_walkable,
    wrap_tile,
    is_wrap_move,
    offscreen_target,
    wrapped_step_direction,
)


class PlayerState:
    """Player game state"""

    def __init__(self, start_tile):
        self.tile = start_tile
        self.target_tile = start_tile
        self.pos = tile_center(start_tile)
        self.start_pos = self.pos.copy()
        self.target_pos = self.pos.copy()

        self.direction = pygame.Vector2(0, 0)
        self.queued_direction = pygame.Vector2(0, 0)
        self.facing_direction = pygame.Vector2(1, 0)

        self.progress = 1.0
        self.wrapping_step = False

        self.score = 0
        self.pellets_eaten = 0
        self.lives = 3

    def reset_position(self, start_tile):
        """Reset to starting position"""
        self.tile = start_tile
        self.target_tile = start_tile
        self.pos = tile_center(start_tile)
        self.start_pos = self.pos.copy()
        self.target_pos = self.pos.copy()
        self.progress = 1.0
        self.wrapping_step = False
        self.direction = pygame.Vector2(0, 0)
        self.queued_direction = pygame.Vector2(0, 0)
        self.facing_direction = pygame.Vector2(1, 0)

    def start_step(self, move_direction):
        """Attempt to start moving in a direction"""
        candidate = next_tile(self.tile, move_direction)
        wrapped_candidate = wrap_tile(candidate)
        should_wrap = is_wrap_move(self.tile, move_direction)

        if not is_walkable(wrapped_candidate):
            return False

        self.direction = move_direction.copy()
        self.facing_direction = move_direction.copy()
        self.target_tile = wrapped_candidate
        self.wrapping_step = should_wrap
        self.start_pos = tile_center(self.tile)

        if self.wrapping_step:
            self.target_pos = offscreen_target(self.tile, move_direction)
        else:
            self.target_pos = tile_center(self.target_tile)

        self.progress = 0.0
        return True

    def update(self):
        """Update player movement"""
        if self.progress >= 1.0:
            if self.queued_direction.length_squared() > 0 and self.start_step(
                self.queued_direction
            ):
                return

            if self.direction.length_squared() > 0 and self.start_step(self.direction):
                return

            self.direction = pygame.Vector2(0, 0)
            self.pos = tile_center(self.tile)
            return

        self.progress = min(1.0, self.progress + PLAYER_SPEED)
        self.pos = self.start_pos.lerp(self.target_pos, self.progress)

        if self.progress >= 1.0:
            self.tile = self.target_tile
            self.pos = tile_center(self.tile)
            self.wrapping_step = False

    def eat_pellets(self, pellets, power_pellets):
        """Check and handle pellet eating"""
        eaten_food = None

        if self.tile in pellets:
            pellets.remove(self.tile)
            self.score += 10
            self.pellets_eaten += 1
            eaten_food = "pellet"

        if self.tile in power_pellets:
            power_pellets.remove(self.tile)
            self.score += 50
            self.pellets_eaten += 1
            eaten_food = "power"

        return eaten_food
