import pygame

from settings import SCREEN_WIDTH, TEXT_COLOR


def draw_attempts(surface: pygame.Surface, font: pygame.font.Font, attempts: int) -> None:
    text = font.render(f"Attempts: {attempts}", True, TEXT_COLOR)
    surface.blit(text, (16, 12))


def draw_center_message(surface: pygame.Surface, big_font: pygame.font.Font, small_font: pygame.font.Font, title: str, subtitle: str) -> None:
    title_surf = big_font.render(title, True, TEXT_COLOR)
    subtitle_surf = small_font.render(subtitle, True, TEXT_COLOR)

    surface.blit(title_surf, (SCREEN_WIDTH // 2 - title_surf.get_width() // 2, 190))
    surface.blit(subtitle_surf, (SCREEN_WIDTH // 2 - subtitle_surf.get_width() // 2, 250))
