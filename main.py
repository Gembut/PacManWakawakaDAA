import sys
import pygame

# Must be called before importing any module that creates pygame fonts/surfaces
pygame.init()

from config import WIDTH, HEIGHT, FPS, GHOST_MOVE_DELAY, RED, CYAN, PURPLE
from map_utils import parse_map
from entities import Pacman, Ghost
from renderer import draw_map, draw_ui


def create_game():
    """Initialise all game objects from the map definition."""
    walls, pellets, pacman_start, ghost_starts = parse_map()

    pacman = Pacman(pacman_start)

    ghosts = [
        Ghost(ghost_starts["astar"], "astar", RED, "A*"),
        Ghost(ghost_starts["bfs"], "bfs", CYAN, "BFS"),
        Ghost(ghost_starts["dijkstra"], "dijkstra", PURPLE, "DIJ"),
    ]

    return walls, pellets, pacman, ghosts, 0, "playing"


def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Pacman AI DAA - A*, BFS, Dijkstra")
    clock = pygame.time.Clock()

    walls, pellets, pacman, ghosts, score, game_state = create_game()
    ghost_move_counter = 0

    while True:
        clock.tick(FPS)

        # ---- Events ----
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            pacman.handle_input(event)

            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                walls, pellets, pacman, ghosts, score, game_state = create_game()
                ghost_move_counter = 0

        # ---- Update ----
        if game_state == "playing":
            pacman.update(walls)

            # Pacman eats pellet
            if pacman.position in pellets:
                pellets.remove(pacman.position)
                score += 10

            # Ghosts move slower than Pacman
            ghost_move_counter += 1
            if ghost_move_counter >= GHOST_MOVE_DELAY:
                for ghost in ghosts:
                    ghost.update(pacman.position, walls)
                ghost_move_counter = 0

            # Collision check
            for ghost in ghosts:
                if ghost.position == pacman.position:
                    game_state = "game_over"

            if len(pellets) == 0:
                game_state = "win"

        # ---- Draw ----
        draw_map(screen, walls, pellets)

        for ghost in ghosts:
            ghost.draw_path_preview(screen)

        pacman.draw(screen)

        for ghost in ghosts:
            ghost.draw(screen)

        draw_ui(screen, score, len(pellets), game_state)

        pygame.display.flip()


if __name__ == "__main__":
    main()
