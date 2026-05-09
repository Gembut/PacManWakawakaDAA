import pygame
from config import (
    TILE_SIZE,
    ROWS,
    COLS,
    WIDTH,
    HEIGHT,
    BLACK,
    NAVY,
    BLUE_WALL,
    WHITE,
    GREEN,
    RED,
)

FONT = pygame.font.SysFont("arial", 18)
BIG_FONT = pygame.font.SysFont("arial", 40, bold=True)


def draw_map(screen, walls, pellets):
    screen.fill(BLACK)

    for y in range(ROWS):
        for x in range(COLS):
            pos = (x, y)
            rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)

            if pos in walls:
                pygame.draw.rect(screen, BLUE_WALL, rect)
                pygame.draw.rect(screen, NAVY, rect, 2)
            else:
                pygame.draw.rect(screen, BLACK, rect)

    for pellet in pellets:
        cx = pellet[0] * TILE_SIZE + TILE_SIZE // 2
        cy = pellet[1] * TILE_SIZE + TILE_SIZE // 2
        pygame.draw.circle(screen, WHITE, (cx, cy), 3)


def draw_ui(screen, score, pellets_left, game_state):
    ui_y = ROWS * TILE_SIZE
    pygame.draw.rect(screen, NAVY, (0, ui_y, WIDTH, 70))

    screen.blit(FONT.render(f"Score: {score}", True, WHITE), (20, ui_y + 10))
    screen.blit(
        FONT.render(f"Pellets Left: {pellets_left}", True, WHITE), (150, ui_y + 10)
    )
    screen.blit(
        FONT.render(
            "Ghost AI: Red=A* | Cyan=BFS | Purple=Dijkstra | Move: WASD / Arrow Keys | R=Restart",
            True,
            WHITE,
        ),
        (20, ui_y + 38),
    )

    if game_state == "game_over":
        _draw_overlay(screen, "GAME OVER", RED)
    elif game_state == "win":
        _draw_overlay(screen, "YOU WIN!", GREEN)


def _draw_overlay(screen, message, color):
    overlay = pygame.Surface((WIDTH, ROWS * TILE_SIZE))
    overlay.set_alpha(180)
    overlay.fill(BLACK)
    screen.blit(overlay, (0, 0))

    text = BIG_FONT.render(message, True, color)
    restart = FONT.render("Press R to Restart", True, WHITE)

    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 80))
    screen.blit(restart, (WIDTH // 2 - restart.get_width() // 2, HEIGHT // 2 - 30))
