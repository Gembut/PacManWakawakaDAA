import pygame
from config import TILE_SIZE, YELLOW
from map_utils import is_walkable


class Pacman:
    def __init__(self, position):
        self.position = position
        self.direction = (0, 0)
        self.next_direction = (0, 0)

    # ------------------------------------------------------------------
    # Input
    # ------------------------------------------------------------------

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            key_map = {
                pygame.K_UP: (0, -1),
                pygame.K_w: (0, -1),
                pygame.K_DOWN: (0, 1),
                pygame.K_s: (0, 1),
                pygame.K_LEFT: (-1, 0),
                pygame.K_a: (-1, 0),
                pygame.K_RIGHT: (1, 0),
                pygame.K_d: (1, 0),
            }
            if event.key in key_map:
                self.next_direction = key_map[event.key]

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def update(self, walls):
        x, y = self.position

        # Try to turn first
        next_pos = (x + self.next_direction[0], y + self.next_direction[1])
        if is_walkable(next_pos, walls):
            self.direction = self.next_direction

        # Move in current direction
        move_pos = (x + self.direction[0], y + self.direction[1])
        if is_walkable(move_pos, walls):
            self.position = move_pos

    # ------------------------------------------------------------------
    # Draw
    # ------------------------------------------------------------------

    def draw(self, screen):
        cx = self.position[0] * TILE_SIZE + TILE_SIZE // 2
        cy = self.position[1] * TILE_SIZE + TILE_SIZE // 2
        pygame.draw.circle(screen, YELLOW, (cx, cy), TILE_SIZE // 2 - 3)
