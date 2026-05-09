import pygame
from config import TILE_SIZE, WHITE, BLACK
from algorithms import astar_path, bfs_path, dijkstra_path

# Registry: add new algorithms here without touching the rest of Ghost
_ALGORITHM_REGISTRY = {
    "astar": astar_path,
    "bfs": bfs_path,
    "dijkstra": dijkstra_path,
}


class Ghost:
    _font = None  # lazy-initialized after pygame.init()

    @classmethod
    def _get_font(cls):
        if cls._font is None:
            cls._font = pygame.font.SysFont("arial", 18)
        return cls._font

    def __init__(self, position, algorithm: str, color, label: str):
        self.position = position
        self.color = color
        self.label = label
        self.path = []

        if algorithm not in _ALGORITHM_REGISTRY:
            raise ValueError(
                f"Unknown algorithm '{algorithm}'. "
                f"Valid options: {list(_ALGORITHM_REGISTRY)}"
            )
        self._find_path = _ALGORITHM_REGISTRY[algorithm]

    # ------------------------------------------------------------------
    # Pathfinding
    # ------------------------------------------------------------------

    def find_path(self, target, walls):
        self.path = self._find_path(self.position, target, walls)

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def update(self, target, walls):
        self.find_path(target, walls)
        if self.path:
            self.position = self.path[0]

    # ------------------------------------------------------------------
    # Draw
    # ------------------------------------------------------------------

    def draw(self, screen):
        x = self.position[0] * TILE_SIZE
        y = self.position[1] * TILE_SIZE

        ghost_rect = pygame.Rect(x + 4, y + 4, TILE_SIZE - 8, TILE_SIZE - 8)
        pygame.draw.rect(screen, self.color, ghost_rect, border_radius=8)

        # Eyes
        pygame.draw.circle(screen, WHITE, (x + 10, y + 11), 4)
        pygame.draw.circle(screen, WHITE, (x + 18, y + 11), 4)
        pygame.draw.circle(screen, BLACK, (x + 10, y + 11), 2)
        pygame.draw.circle(screen, BLACK, (x + 18, y + 11), 2)

        # Algorithm label — font is safely initialized here, after pygame.init()
        text = self._get_font().render(self.label, True, WHITE)
        screen.blit(text, (x - 2, y - 18))

    def draw_path_preview(self, screen, steps: int = 8):
        """Draw the first `steps` tiles of the planned path."""
        for pos in self.path[:steps]:
            cx = pos[0] * TILE_SIZE + TILE_SIZE // 2
            cy = pos[1] * TILE_SIZE + TILE_SIZE // 2
            pygame.draw.circle(screen, self.color, (cx, cy), 4)
