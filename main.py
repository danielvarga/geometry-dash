import asyncio
from enum import Enum, auto

import pygame

from camera import compute_camera_x
from level import draw_level, load_level
from player import Player
from settings import BACKGROUND_COLOR, FPS, LEVEL_PATH, SCREEN_HEIGHT, SCREEN_WIDTH, WINDOW_TITLE
from ui import draw_attempts, draw_center_message


class GameState(Enum):
    MENU = auto()
    PLAYING = auto()
    DEAD = auto()
    WIN = auto()


async def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(WINDOW_TITLE)
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("freesansbold", 26)
    big_font = pygame.font.SysFont("freesansbold", 54)

    level = load_level(LEVEL_PATH)
    player = Player(*level.start_pos)

    state = GameState.MENU
    attempts = 1
    camera_x = 0
    running = True
    jump_held = False
    mouse_held = False

    while running:
        dt = min(clock.tick(FPS) / 1000.0, 1 / 30)
        jump_pressed = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    continue
                if event.key == pygame.K_SPACE:
                    jump_held = True
                    jump_pressed = True
            elif event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
                jump_held = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_held = True
                jump_pressed = True
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                mouse_held = False

        if jump_pressed:
            if state == GameState.MENU:
                state = GameState.PLAYING
            elif state == GameState.PLAYING:
                player.request_jump()
            elif state in (GameState.DEAD, GameState.WIN):
                if state == GameState.DEAD:
                    attempts += 1
                player.reset(*level.start_pos)
                state = GameState.PLAYING

        if state == GameState.PLAYING:
            player.update(dt, level.solids, jump_held or mouse_held)

            for spike in level.spike_hitboxes:
                if player.rect.colliderect(spike):
                    state = GameState.DEAD
                    break

            if player.hit_head:
                state = GameState.DEAD
            if player.hit_wall:
                state = GameState.DEAD

            if player.rect.top > SCREEN_HEIGHT:
                state = GameState.DEAD

            if player.rect.colliderect(level.end_zone):
                state = GameState.WIN

            camera_x = compute_camera_x(player.rect.centerx, level.width_px)

        screen.fill(BACKGROUND_COLOR)
        draw_level(screen, level, camera_x)
        player.draw(screen, camera_x)
        draw_attempts(screen, font, attempts)

        if state == GameState.MENU:
            draw_center_message(screen, big_font, font, "Geometry Dash Clone", "Press Space or Click to Start")
        elif state == GameState.DEAD:
            draw_center_message(screen, big_font, font, "You Died", "Press Space or Click to Retry")
        elif state == GameState.WIN:
            draw_center_message(screen, big_font, font, "Level Complete", "Press Space or Click to Play Again")

        pygame.display.flip()
        # Required for browser/pygbag event loop cooperation.
        await asyncio.sleep(0)

    pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())
