from dataclasses import dataclass
from pathlib import Path

import pygame

from settings import END_COLOR, GROUND_COLOR, SCREEN_HEIGHT, SPIKE_COLOR, TILE_SIZE


@dataclass
class LevelData:
    solids: list[pygame.Rect]
    spikes: list[pygame.Rect]
    end_zone: pygame.Rect
    start_pos: tuple[int, int]
    width_px: int


def load_level(path: Path) -> LevelData:
    raw_lines = [line.rstrip("\n") for line in path.read_text().splitlines() if line.strip()]
    if not raw_lines:
        raise ValueError(f"Level file {path} is empty.")

    width = max(len(line) for line in raw_lines)
    lines = [line.ljust(width, ".") for line in raw_lines]

    solids: list[pygame.Rect] = []
    spikes: list[pygame.Rect] = []
    end_zone: pygame.Rect | None = None
    start_pos: tuple[int, int] | None = None

    for row, line in enumerate(lines):
        for col, char in enumerate(line):
            x = col * TILE_SIZE
            y = row * TILE_SIZE
            tile = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)

            if char == "#":
                solids.append(tile)
            elif char == "^":
                spikes.append(tile)
            elif char == "S":
                start_pos = (x, y)
            elif char == "E":
                end_zone = tile

    if start_pos is None:
        raise ValueError("Level is missing 'S' start marker.")
    if end_zone is None:
        raise ValueError("Level is missing 'E' end marker.")

    width_px = width * TILE_SIZE
    return LevelData(solids=solids, spikes=spikes, end_zone=end_zone, start_pos=start_pos, width_px=width_px)


def draw_level(surface: pygame.Surface, level: LevelData, camera_x: int) -> None:
    for solid in level.solids:
        pygame.draw.rect(surface, GROUND_COLOR, solid.move(-camera_x, 0))

    for spike in level.spikes:
        sx = spike.x - camera_x
        sy = spike.y
        points = [
            (sx + spike.width // 2, sy),
            (sx + spike.width, sy + spike.height),
            (sx, sy + spike.height),
        ]
        pygame.draw.polygon(surface, SPIKE_COLOR, points)

    pygame.draw.rect(surface, END_COLOR, level.end_zone.move(-camera_x, 0), border_radius=6)

    floor_y = (SCREEN_HEIGHT // TILE_SIZE - 1) * TILE_SIZE
    pygame.draw.rect(surface, GROUND_COLOR, (0, floor_y, surface.get_width(), SCREEN_HEIGHT - floor_y))
