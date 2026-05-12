"""
All rendering/drawing functions
"""

import math
import pygame
from config import (
    WIDTH,
    MAZE_HEIGHT,
    HEIGHT,
    HUD_HEIGHT,
    TILE_SIZE,
    BLACK,
    BLUE,
    BLUE_DARK,
    YELLOW,
    WHITE,
    PELLET,
    POWER_PELLET,
    RED,
    CYAN,
    PINK,
    FRIGHTENED_BLUE,
    HUD_TEXT,
    FONT,
    SMALL_FONT,
    TITLE_FONT,
)


def draw_background(screen):
    """Draw grid background"""
    screen.fill(BLACK)

    for y in range(0, MAZE_HEIGHT, TILE_SIZE):
        pygame.draw.line(screen, (6, 6, 22), (0, y), (WIDTH, y))

    for x in range(0, WIDTH, TILE_SIZE):
        pygame.draw.line(screen, (6, 6, 22), (x, 0), (x, MAZE_HEIGHT))


def draw_walls(screen, walls):
    """Draw all wall tiles"""
    for wall in walls:
        pygame.draw.rect(screen, BLUE, wall)
        inner = wall.inflate(-8, -8)
        pygame.draw.rect(screen, BLUE_DARK, inner)
        pygame.draw.rect(screen, CYAN, wall, 1)


def draw_pellets(screen, pellets, power_pellets):
    """Draw all pellets and power pellets"""
    for col, row in pellets:
        center = (
            col * TILE_SIZE + TILE_SIZE // 2,
            row * TILE_SIZE + TILE_SIZE // 2,
        )
        pygame.draw.circle(screen, PELLET, center, 3)

    pulse = 1 + int((pygame.time.get_ticks() // 180) % 2)
    for col, row in power_pellets:
        center = (
            col * TILE_SIZE + TILE_SIZE // 2,
            row * TILE_SIZE + TILE_SIZE // 2,
        )
        pygame.draw.circle(screen, POWER_PELLET, center, 7 + pulse)
        pygame.draw.circle(screen, PINK, center, 4 + pulse)


def draw_ghost_cage(screen):
    """Draw the ghost cage"""
    cage_rect = pygame.Rect(8 * TILE_SIZE, 8 * TILE_SIZE, 5 * TILE_SIZE, 3 * TILE_SIZE)
    inner_rect = cage_rect.inflate(-10, -8)
    door_rect = pygame.Rect(10 * TILE_SIZE, 8 * TILE_SIZE + 9, TILE_SIZE, 10)

    pygame.draw.rect(screen, BLACK, inner_rect)
    pygame.draw.rect(screen, BLUE, cage_rect, 4)
    pygame.draw.rect(screen, CYAN, cage_rect.inflate(-5, -5), 1)

    pygame.draw.rect(screen, PINK, door_rect)
    pygame.draw.line(screen, WHITE, door_rect.topleft, door_rect.topright, 1)


def draw_ghost(screen, center, color):
    """Draw a ghost sprite"""
    x, y = center
    top = y - 13
    bottom = y + 12
    left = x - 11
    right = x + 11

    body_points = [
        (x, top),
        (x + 6, top + 2),
        (right, top + 9),
        (right, bottom - 5),
        (x + 8, bottom),
        (x + 4, bottom - 5),
        (x, bottom),
        (x - 4, bottom - 5),
        (x - 8, bottom),
        (left, bottom - 5),
        (left, top + 9),
        (x - 6, top + 2),
    ]

    shadow_points = [(px + 2, py + 2) for px, py in body_points]
    pygame.draw.polygon(screen, (0, 0, 0), shadow_points)
    pygame.draw.polygon(screen, color, body_points)
    pygame.draw.circle(screen, color, (x, top + 11), 11)
    pygame.draw.rect(screen, color, (left, top + 11, 22, 14))

    pygame.draw.line(screen, WHITE, (x - 6, top + 3), (x - 1, top + 1), 2)

    pygame.draw.ellipse(screen, WHITE, (x - 8, y - 8, 7, 9))
    pygame.draw.ellipse(screen, WHITE, (x + 2, y - 8, 7, 9))
    pygame.draw.circle(screen, BLUE_DARK, (x - 4, y - 4), 2)
    pygame.draw.circle(screen, BLUE_DARK, (x + 6, y - 4), 2)

    pygame.draw.line(screen, BLACK, (left + 2, bottom - 1), (right - 2, bottom - 1), 1)


def draw_ghost_eyes(screen, center):
    """Draw just the eyes of a ghost (for eaten state)"""
    x, y = center
    pygame.draw.ellipse(screen, WHITE, (x - 9, y - 8, 8, 10))
    pygame.draw.ellipse(screen, WHITE, (x + 2, y - 8, 8, 10))
    pygame.draw.circle(screen, BLUE_DARK, (x - 4, y - 4), 2)
    pygame.draw.circle(screen, BLUE_DARK, (x + 7, y - 4), 2)


def draw_ghosts(screen, ghosts, is_frightened, frightened_timer):
    """Draw all ghosts"""
    for ghost in ghosts:
        center = (round(ghost["pos"].x), round(ghost["pos"].y + 2))

        if ghost["eaten"]:
            draw_ghost_eyes(screen, center)
        elif is_frightened and ghost["active"]:
            flashing = frightened_timer < 360 and (frightened_timer // 10) % 2 == 0
            draw_ghost(screen, center, WHITE if flashing else FRIGHTENED_BLUE)
        else:
            draw_ghost(screen, center, ghost["color"])

        label_color = WHITE if ghost["active"] else HUD_TEXT
        label_text = (
            ghost["name"]
            if ghost["active"]
            else f"{ghost['name']} {ghost['release_at']}"
        )
        label = SMALL_FONT.render(label_text, False, label_color)
        label_x = center[0] - label.get_width() // 2
        label_y = center[1] - 31
        pygame.draw.rect(
            screen,
            BLACK,
            (label_x - 2, label_y - 1, label.get_width() + 4, label.get_height() + 1),
        )
        screen.blit(label, (label_x, label_y))


def draw_player(screen, player_pos, facing_direction, mouth_open, player_radius):
    """Draw the player (Pac-Man)"""
    center = (round(player_pos.x), round(player_pos.y))

    angle = 0
    if facing_direction.x < 0:
        angle = 180
    elif facing_direction.y < 0:
        angle = 90
    elif facing_direction.y > 0:
        angle = 270

    pygame.draw.circle(screen, YELLOW, center, player_radius)

    if mouth_open:
        mouth_size = 38
        angle1 = math.radians(angle - mouth_size)
        angle2 = math.radians(angle + mouth_size)

        p1 = center
        p2 = (
            center[0] + math.cos(angle1) * player_radius * 1.5,
            center[1] - math.sin(angle1) * player_radius * 1.5,
        )
        p3 = (
            center[0] + math.cos(angle2) * player_radius * 1.5,
            center[1] - math.sin(angle2) * player_radius * 1.5,
        )
        pygame.draw.polygon(screen, BLACK, [p1, p2, p3])


def draw_death_animation(
    screen, player_pos, facing_direction, death_timer, death_duration, player_radius
):
    """Draw death animation"""
    progress = min(1.0, death_timer / death_duration)
    center = (round(player_pos.x), round(player_pos.y))
    radius = max(2, int(player_radius * (1.0 - progress * 0.65)))
    mouth_size = 25 + progress * 155

    pygame.draw.circle(screen, YELLOW, center, radius)

    angle = 0
    if facing_direction.x < 0:
        angle = 180
    elif facing_direction.y < 0:
        angle = 90
    elif facing_direction.y > 0:
        angle = 270

    angle1 = math.radians(angle - mouth_size)
    angle2 = math.radians(angle + mouth_size)
    p2 = (
        center[0] + math.cos(angle1) * player_radius * 1.8,
        center[1] - math.sin(angle1) * player_radius * 1.8,
    )
    p3 = (
        center[0] + math.cos(angle2) * player_radius * 1.8,
        center[1] - math.sin(angle2) * player_radius * 1.8,
    )
    pygame.draw.polygon(screen, BLACK, [center, p2, p3])

    spark_count = 8
    spark_length = int(8 + progress * 15)
    for i in range(spark_count):
        spark_angle = (math.tau / spark_count) * i + progress * 3
        inner = (
            center[0] + math.cos(spark_angle) * (player_radius + 2),
            center[1] + math.sin(spark_angle) * (player_radius + 2),
        )
        outer = (
            center[0] + math.cos(spark_angle) * (player_radius + spark_length),
            center[1] + math.sin(spark_angle) * (player_radius + spark_length),
        )
        pygame.draw.line(screen, YELLOW, inner, outer, 2)


def draw_hud(screen, score, lives, is_frightened, frightened_timer):
    """Draw the HUD (heads-up display)"""
    hud_y = MAZE_HEIGHT
    pygame.draw.rect(screen, BLACK, (0, hud_y, WIDTH, HUD_HEIGHT))
    pygame.draw.line(screen, BLUE, (0, hud_y), (WIDTH, hud_y), 3)
    pygame.draw.line(screen, BLUE_DARK, (0, hud_y + 4), (WIDTH, hud_y + 4), 2)

    score_text = FONT.render(f"SCORE {score:04}", False, WHITE)
    title_text = TITLE_FONT.render("PAC-MAN", False, YELLOW)
    if is_frightened:
        move_text = SMALL_FONT.render(
            f"POWER {math.ceil(frightened_timer / 60)}", False, FRIGHTENED_BLUE
        )
    else:
        move_text = SMALL_FONT.render("GRID MOVE: ARROWS / WASD", False, HUD_TEXT)
    lives_text = SMALL_FONT.render("LIVES", False, WHITE)

    screen.blit(score_text, (14, hud_y + 12))
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, hud_y + 8))
    screen.blit(move_text, (WIDTH // 2 - move_text.get_width() // 2, hud_y + 40))
    screen.blit(lives_text, (WIDTH - 122, hud_y + 14))

    for i in range(lives):
        x = WIDTH - 100 + i * 24
        y = hud_y + 42
        pygame.draw.circle(screen, YELLOW, (x, y), 8)
        pygame.draw.polygon(screen, BLACK, [(x, y), (x + 10, y - 5), (x + 10, y + 5)])


def draw_center_message(screen, title, subtitle=None, color=WHITE, border_color=BLUE):
    """Draw a centered message box"""
    panel = pygame.Rect(76, HEIGHT // 2 - 72, WIDTH - 152, 110)
    pygame.draw.rect(screen, BLACK, panel)
    pygame.draw.rect(screen, border_color, panel, 4)

    title_text = TITLE_FONT.render(title, False, color)
    screen.blit(
        title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 2 - 42)
    )

    if subtitle:
        sub_text = SMALL_FONT.render(subtitle, False, WHITE)
        screen.blit(sub_text, (WIDTH // 2 - sub_text.get_width() // 2, HEIGHT // 2 - 7))


def draw_countdown_message(screen, game_state, countdown_timer, fps):
    """Draw countdown message"""
    if game_state != "countdown":
        return

    remaining = math.ceil(countdown_timer / fps)
    title = "READY!" if remaining <= 0 else str(remaining)
    draw_center_message(screen, title, "GET READY", YELLOW, BLUE)


def draw_win_message(screen, remaining_food):
    """Draw win message overlay"""
    if remaining_food > 0:
        return

    overlay = pygame.Surface((WIDTH, MAZE_HEIGHT))
    overlay.set_alpha(190)
    overlay.fill(BLACK)
    screen.blit(overlay, (0, 0))

    panel = pygame.Rect(34, HEIGHT // 2 - 70, WIDTH - 68, 110)
    pygame.draw.rect(screen, BLACK, panel)
    pygame.draw.rect(screen, BLUE, panel, 4)

    text = FONT.render("YOU CLEARED THE MAP!", False, YELLOW)
    sub = SMALL_FONT.render("R RESTART   ESC QUIT", False, WHITE)

    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 42))
    screen.blit(sub, (WIDTH // 2 - sub.get_width() // 2, HEIGHT // 2 - 6))


def draw_game_over_message(screen, game_over):
    """Draw game over message overlay"""
    if not game_over:
        return

    overlay = pygame.Surface((WIDTH, MAZE_HEIGHT))
    overlay.set_alpha(205)
    overlay.fill(BLACK)
    screen.blit(overlay, (0, 0))

    panel = pygame.Rect(46, HEIGHT // 2 - 70, WIDTH - 92, 110)
    pygame.draw.rect(screen, BLACK, panel)
    pygame.draw.rect(screen, RED, panel, 4)

    text = FONT.render("GAME OVER", False, RED)
    sub = SMALL_FONT.render("R RESTART   ESC QUIT", False, WHITE)

    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 42))
    screen.blit(sub, (WIDTH // 2 - sub.get_width() // 2, HEIGHT // 2 - 6))
