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
from logic.audio import SoundManager
from map import GAME_MAPS, next_tile, wrap_tile
from character.ghost import update_ghost
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
    draw_menu,
    draw_win_message,
    draw_game_over_message,
)


def player_is_moving_toward_food(player, pellets, power_pellets):
    """Check whether Pac-Man is continuing into a tile that still has food."""
    if player.direction.length_squared() == 0:
        return False

    next_food_tile = wrap_tile(next_tile(player.tile, player.direction))
    return next_food_tile in pellets or next_food_tile in power_pellets


def check_ghost_collision(player, ghosts, is_frightened, game_state):
    """Check collisions between player and ghosts"""
    for ghost in ghosts:
        if not ghost["active"] and not ghost["eaten"]:
            continue

        distance = player.pos.distance_to(ghost["pos"])
        if distance < PLAYER_RADIUS + 9:
            if (
                is_frightened
                and not ghost["eaten"]
                and not ghost.get("ignore_frightened")
            ):
                player.score += game_state.ghost_eat_score
                game_state.ghost_eat_score *= 2
                ghost["eaten"] = True
                ghost["active"] = True
                ghost["progress"] = 1.0
                return "eat_ghost"

            if ghost["eaten"]:
                continue

            return "death"

    return None


def main():
    """Main game loop"""
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Pac-Man Retro")

    clock = pygame.time.Clock()

    # Initialize game state
    selected_map = 0
    game = GameState(selected_map)
    sounds = SoundManager()
    sounds.loop_event("coffee_break")
    screen_state = "menu"
    win_sound_played = False

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
                elif screen_state == "menu":
                    if event.key in [pygame.K_DOWN, pygame.K_RIGHT, pygame.K_d]:
                        selected_map = (selected_map + 1) % len(GAME_MAPS)
                        sounds.play_once("credit")
                    elif event.key in [pygame.K_UP, pygame.K_LEFT, pygame.K_a]:
                        selected_map = (selected_map - 1) % len(GAME_MAPS)
                        sounds.play_once("credit")
                    elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                        game.restart_game(selected_map)
                        sounds.play_exclusive("start")
                        screen_state = "game"
                        win_sound_played = False
                elif event.key == pygame.K_r and (
                    game.game_over or game.remaining_food() == 0
                ):
                    sounds.stop_all()
                    sounds.loop_event("coffee_break")
                    screen_state = "menu"
                    win_sound_played = False
                elif event.key == pygame.K_m:
                    screen_state = "menu"
                    sounds.stop_all()
                    sounds.loop_event("coffee_break")
                    win_sound_played = False
                elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                    game.player.queued_direction = DIRECTIONS["right"].copy()
                elif event.key in [pygame.K_LEFT, pygame.K_a]:
                    game.player.queued_direction = DIRECTIONS["left"].copy()
                elif event.key in [pygame.K_UP, pygame.K_w]:
                    game.player.queued_direction = DIRECTIONS["up"].copy()
                elif event.key in [pygame.K_DOWN, pygame.K_s]:
                    game.player.queued_direction = DIRECTIONS["down"].copy()

        if screen_state == "menu":
            sounds.loop_event("coffee_break")

        # Update game logic
        elif (
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
                if game.game_state == "countdown":
                    sounds.play_exclusive("start")

        elif (
            game.game_state == "playing"
            and game.remaining_food() > 0
            and not game.game_over
        ):
            game.elapsed_frames += 1
            game.update_ghost_release_cooldown()

            # Update player
            game.player.update()

            # Update ghosts
            if game.frightened_timer > 0:
                game.frightened_timer -= 1
                if game.frightened_timer == 0:
                    for ghost in game.ghosts:
                        ghost["ignore_frightened"] = False
                        ghost["waiting_for_power_end"] = False

            for ghost in game.ghosts:
                update_ghost(ghost, game.player.tile, game.is_frightened(), find_path)

            # Check pellet eating
            eaten_food = game.player.eat_pellets(
                game.pellets, game.power_pellets
            )
            pellet_was_eaten = eaten_food is not None

            # Handle power pellet activation
            if eaten_food == "power":
                game.activate_power_mode()

            # Release one eligible ghost each time Pac-Man eats a pellet.
            if pellet_was_eaten:
                sounds.start_waka()

            game.try_release_ghost()

            is_eating_sequence = pellet_was_eaten or player_is_moving_toward_food(
                game.player, game.pellets, game.power_pellets
            )
            if not is_eating_sequence:
                sounds.stop_waka()

            # Check ghost collisions
            collision_result = check_ghost_collision(
                game.player, game.ghosts, game.is_frightened(), game
            )
            if collision_result == "eat_ghost":
                sounds.stop_waka()
                sounds.play_once("eat_ghost")
            elif collision_result == "death":
                sounds.play_exclusive("death")
                game.game_state = "dying"
                game.death_timer = 0
                game.player.direction = pygame.Vector2(0, 0)
                game.player.queued_direction = pygame.Vector2(0, 0)

        # Update mouth animation
        game.mouth_timer += 1
        if game.mouth_timer > 8:
            game.mouth_open = not game.mouth_open
            game.mouth_timer = 0

        if screen_state != "game" or game.game_state not in ["playing", "countdown"]:
            sounds.stop_waka()

        if screen_state == "game" and game.remaining_food() == 0 and not win_sound_played:
            sounds.play_exclusive("coffee_break")
            win_sound_played = True

        has_eaten_ghosts = any(ghost["eaten"] for ghost in game.ghosts)
        has_frightened_ghosts = any(
            ghost["active"] and not ghost["eaten"] and not ghost.get("ignore_frightened")
            for ghost in game.ghosts
        )
        audio_game_state = (
            "playing"
            if screen_state == "game"
            and game.game_state == "playing"
            and game.remaining_food() > 0
            else "win" if game.remaining_food() == 0 else game.game_state
        )
        sounds.update_ghost_loop(
            audio_game_state,
            game.is_frightened() and has_frightened_ghosts,
            has_eaten_ghosts,
        )

        # Render
        if screen_state == "menu":
            draw_menu(screen, GAME_MAPS, selected_map, pygame.time.get_ticks() // 16)
        else:
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
                game.elapsed_frames // FPS,
            )
            draw_countdown_message(screen, game.game_state, game.countdown_timer, FPS)
            draw_win_message(screen, game.remaining_food())
            draw_game_over_message(screen, game.game_over)

        pygame.display.flip()

    from report_generator import AlgorithmReport

    AlgorithmReport.save_report("algorithm_report.txt")

    import os

    file_exists = os.path.exists("algorithm_metrics.csv")
    with open("algorithm_metrics.csv", "a") as f:
        if not file_exists:
            f.write(
                "Algorithm,Calls,Successful_Searches,Failed_Searches,Avg_Time_ms,Avg_Path_Length,Total_Time_ms,Avg_Nodes_Explored\n"
            )
        # write only the data rows, skip the header
        csv_content = AlgorithmReport.generate_csv_report()
        rows = csv_content.split("\n")[1:]  # skip header line
        f.write("\n".join(rows) + "\n\n")

    print("Reports saved.")

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
