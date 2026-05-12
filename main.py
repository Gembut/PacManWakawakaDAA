"""
Main game loop and collision detection
"""

import sys
import pygame
from config import (
    WIDTH,
    HEIGHT,
    FPS,
    COUNTDOWN_SECONDS,
    DEATH_DURATION,
    PLAYER_RADIUS,
    DIRECTIONS,
)
from logic.game_state import GameState
from map import tile_center
from character.ghost import update_ghost, release_ghosts
from algorithm.pathfinding import find_path
from logic.render import (
    draw_background,
    draw_walls,
    draw_pellets,
    draw_ghost_cage,
    draw_ghosts,
    draw_player,
    draw_death_animation,
    draw_hud,
    draw_countdown_message,
    draw_win_message,
    draw_game_over_message,
)


def check_ghost_collision(player, ghosts, is_frightened, game_state):
    """Check collisions between player and ghosts"""
    for ghost in ghosts:
        if not ghost["active"] and not ghost["eaten"]:
            continue

        distance = player.pos.distance_to(ghost["pos"])
        if distance < PLAYER_RADIUS + 9:
            if is_frightened and not ghost["eaten"]:
                player.score += game_state.ghost_eat_score
                game_state.ghost_eat_score *= 2
                ghost["eaten"] = True
                ghost["active"] = True
                ghost["progress"] = 1.0
                return

            if ghost["eaten"]:
                continue

            return True  # Collision!

    return False


def main():
    """Main game loop"""
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Pac-Man Retro")

    clock = pygame.time.Clock()

    # Initialize game state
    game = GameState()

    running = True
    while running:
        clock.tick(FPS)

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r and (
                    game.game_over or game.remaining_food() == 0
                ):
                    game.restart_game()
                elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                    game.player.queued_direction = DIRECTIONS["right"].copy()
                elif event.key in [pygame.K_LEFT, pygame.K_a]:
                    game.player.queued_direction = DIRECTIONS["left"].copy()
                elif event.key in [pygame.K_UP, pygame.K_w]:
                    game.player.queued_direction = DIRECTIONS["up"].copy()
                elif event.key in [pygame.K_DOWN, pygame.K_s]:
                    game.player.queued_direction = DIRECTIONS["down"].copy()

        # Update game logic
        if (
            game.game_state == "countdown"
            and game.remaining_food() > 0
            and not game.game_over
        ):
            game.countdown_timer -= 1
            if game.countdown_timer <= 0:
                game.game_state = "playing"

        elif game.game_state == "dying":
            game.death_timer += 1
            if game.death_timer >= game.death_duration:
                game.handle_death()

        elif (
            game.game_state == "playing"
            and game.remaining_food() > 0
            and not game.game_over
        ):
            # Update player
            game.player.update()

            # Update ghosts
            if game.frightened_timer > 0:
                game.frightened_timer -= 1

            for ghost in game.ghosts:
                update_ghost(ghost, game.player.tile, game.is_frightened(), find_path)

            # Check pellet eating
            pellets_eaten = game.player.eat_pellets(game.pellets, game.power_pellets)

            # Handle power pellet activation
            if game.player.tile in game.initial_power_pellets:
                if game.player.tile not in game.power_pellets:  # Just eaten
                    game.activate_power_mode()

            # Release ghosts as pellets are eaten
            release_ghosts(game.ghosts, game.player.pellets_eaten)

            # Check ghost collisions
            if check_ghost_collision(
                game.player, game.ghosts, game.is_frightened(), game
            ):
                game.game_state = "dying"
                game.death_timer = 0
                game.player.direction = pygame.Vector2(0, 0)
                game.player.queued_direction = pygame.Vector2(0, 0)

        # Update mouth animation
        game.mouth_timer += 1
        if game.mouth_timer > 8:
            game.mouth_open = not game.mouth_open
            game.mouth_timer = 0

        # Render
        draw_background(screen)
        draw_pellets(screen, game.pellets, game.power_pellets)
        draw_walls(screen, game.walls)
        draw_ghost_cage(screen)
        draw_ghosts(screen, game.ghosts, game.is_frightened(), game.frightened_timer)

        if game.game_state == "dying":
            draw_death_animation(
                screen,
                game.player.pos,
                game.player.facing_direction,
                game.death_timer,
                game.death_duration,
                PLAYER_RADIUS,
            )
        else:
            draw_player(
                screen,
                game.player.pos,
                game.player.facing_direction,
                game.mouth_open,
                PLAYER_RADIUS,
            )

        draw_hud(
            screen,
            game.player.score,
            game.player.lives,
            game.is_frightened(),
            game.frightened_timer,
        )
        draw_countdown_message(screen, game.game_state, game.countdown_timer, FPS)
        draw_win_message(screen, game.remaining_food())
        draw_game_over_message(screen, game.game_over)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
