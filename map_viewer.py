from __future__ import annotations

import sys
from pathlib import Path

import pygame

from settings import (
    BACKGROUND_COLOR,
    BASE_DIR,
    END_COLOR,
    GROUND_COLOR,
    LEVEL_PATH,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    SPIKE_COLOR,
    TILE_SIZE,
)


MARGIN = 24
MIN_ZOOM = 0.08
MAX_ZOOM = 8.0
GRID_COLOR = (71, 85, 105)
START_COLOR = (59, 130, 246)
TEXT_COLOR = (241, 245, 249)
SELECTED_COLOR = (250, 204, 21)

EDITABLE_TILES = [".", "#", "^", "S", "E"]
TILE_LABELS = {
    ".": "Empty",
    "#": "Solid",
    "^": "Spike",
    "S": "Start",
    "E": "End",
}
KEY_TO_TILE = {
    pygame.K_1: ".",
    pygame.K_2: "#",
    pygame.K_3: "^",
    pygame.K_4: "S",
    pygame.K_5: "E",
}


def has_command_mod(mods: int) -> bool:
    return bool(mods & (pygame.KMOD_CTRL | pygame.KMOD_META | pygame.KMOD_GUI))


def is_save_shortcut(event: pygame.event.Event) -> bool:
    if event.key != pygame.K_s:
        return False
    return has_command_mod(event.mod)


def resolve_level_path() -> Path:
    if len(sys.argv) > 1:
        level_arg = Path(sys.argv[1])
        if not level_arg.is_absolute():
            level_arg = BASE_DIR / level_arg
        return level_arg
    return LEVEL_PATH


def load_grid(path: Path) -> list[list[str]]:
    raw_lines = [line.rstrip("\n") for line in path.read_text().splitlines() if line.strip()]
    if not raw_lines:
        raise ValueError(f"Level file {path} is empty.")
    width = max(len(line) for line in raw_lines)
    return [list(line.ljust(width, ".")) for line in raw_lines]


def save_grid(path: Path, grid: list[list[str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["".join(row) for row in grid]
    path.write_text("\n".join(lines) + "\n")


def find_tile(grid: list[list[str]], tile: str) -> tuple[int, int] | None:
    for row_idx, row in enumerate(grid):
        for col_idx, value in enumerate(row):
            if value == tile:
                return row_idx, col_idx
    return None


def build_world_surface(grid: list[list[str]]) -> pygame.Surface:
    rows = len(grid)
    cols = len(grid[0]) if rows else 1
    surface = pygame.Surface((max(1, cols * TILE_SIZE), max(1, rows * TILE_SIZE)), pygame.SRCALPHA)
    surface.fill(BACKGROUND_COLOR)

    for row_idx, row in enumerate(grid):
        for col_idx, tile in enumerate(row):
            x = col_idx * TILE_SIZE
            y = row_idx * TILE_SIZE
            rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
            if tile == "#":
                pygame.draw.rect(surface, GROUND_COLOR, rect)
            elif tile == "^":
                points = [
                    (x + TILE_SIZE // 2, y),
                    (x + TILE_SIZE, y + TILE_SIZE),
                    (x, y + TILE_SIZE),
                ]
                pygame.draw.polygon(surface, SPIKE_COLOR, points)
            elif tile == "E":
                pygame.draw.rect(surface, END_COLOR, rect, border_radius=5)
            elif tile == "S":
                pygame.draw.rect(surface, START_COLOR, rect, border_radius=5)
    return surface


def fit_zoom(window_size: tuple[int, int], world_size: tuple[int, int]) -> float:
    win_w, win_h = window_size
    world_w, world_h = world_size
    if world_w <= 0 or world_h <= 0:
        return 1.0
    scale_x = max(1.0, win_w - MARGIN * 2) / world_w
    scale_y = max(1.0, win_h - MARGIN * 2) / world_h
    return max(MIN_ZOOM, min(MAX_ZOOM, min(scale_x, scale_y)))


def screen_to_cell(
    mouse_pos: tuple[int, int],
    draw_x: int,
    draw_y: int,
    zoom: float,
    cols: int,
    rows: int,
) -> tuple[int, int] | None:
    mx, my = mouse_pos
    world_x = (mx - draw_x) / zoom
    world_y = (my - draw_y) / zoom
    col = int(world_x // TILE_SIZE)
    row = int(world_y // TILE_SIZE)
    if row < 0 or row >= rows or col < 0 or col >= cols:
        return None
    return row, col


def place_tile(grid: list[list[str]], row: int, col: int, tile: str) -> bool:
    current = grid[row][col]
    if tile not in EDITABLE_TILES:
        return False
    if current == tile:
        return False

    if tile in ("S", "E"):
        existing = find_tile(grid, tile)
        if existing is not None:
            erow, ecol = existing
            grid[erow][ecol] = "."

    grid[row][col] = tile
    return True


def draw_grid_overlay(surface: pygame.Surface, draw_x: int, draw_y: int, cols: int, rows: int, zoom: float) -> None:
    if zoom < 0.3:
        return
    tile_px = max(1, int(TILE_SIZE * zoom))
    for col in range(cols + 1):
        x = draw_x + col * tile_px
        pygame.draw.line(surface, GRID_COLOR, (x, draw_y), (x, draw_y + rows * tile_px), 1)
    for row in range(rows + 1):
        y = draw_y + row * tile_px
        pygame.draw.line(surface, GRID_COLOR, (draw_x, y), (draw_x + cols * tile_px, y), 1)


def ensure_required_markers(grid: list[list[str]]) -> None:
    rows = len(grid)
    cols = len(grid[0]) if rows else 0
    if rows == 0 or cols == 0:
        return
    if find_tile(grid, "S") is None:
        grid[max(0, rows - 2)][0] = "S"
    if find_tile(grid, "E") is None:
        grid[max(0, rows - 2)][max(0, cols - 1)] = "E"


def main() -> None:
    level_path = resolve_level_path()
    if not level_path.exists():
        raise FileNotFoundError(f"Level file not found: {level_path}")

    pygame.init()
    pygame.display.set_caption(f"Level Editor - {level_path.name}")
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("freesansbold", 18)

    grid = load_grid(level_path)
    ensure_required_markers(grid)

    zoom = fit_zoom(screen.get_size(), (len(grid[0]) * TILE_SIZE, len(grid) * TILE_SIZE))
    pan_x = 0.0
    pan_y = 0.0
    selected_tile = "^"
    dirty = False
    status_message = ""
    status_timer = 0.0
    running = True
    left_mouse_down = False
    right_mouse_down = False

    while running:
        dt = min(clock.tick(120) / 1000.0, 1 / 20)
        rows = len(grid)
        cols = len(grid[0]) if rows else 1
        world = build_world_surface(grid)
        world_rect = world.get_rect()

        scaled_w = max(1, int(world_rect.width * zoom))
        scaled_h = max(1, int(world_rect.height * zoom))
        center_x = (screen.get_width() - scaled_w) // 2
        center_y = (screen.get_height() - scaled_h) // 2
        draw_x = center_x - int(pan_x * zoom)
        draw_y = center_y - int(pan_y * zoom)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key in (pygame.K_EQUALS, pygame.K_PLUS, pygame.K_KP_PLUS):
                    zoom = min(MAX_ZOOM, zoom * 1.15)
                elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                    zoom = max(MIN_ZOOM, zoom / 1.15)
                elif event.key == pygame.K_f:
                    zoom = fit_zoom(screen.get_size(), world.get_size())
                    pan_x = 0.0
                    pan_y = 0.0
                elif event.key in KEY_TO_TILE:
                    selected_tile = KEY_TO_TILE[event.key]
                elif is_save_shortcut(event):
                    ensure_required_markers(grid)
                    save_grid(level_path, grid)
                    dirty = False
                    status_message = "Saved"
                    status_timer = 1.25
                elif event.key == pygame.K_r:
                    grid = load_grid(level_path)
                    ensure_required_markers(grid)
                    dirty = False
                    status_message = "Reloaded"
                    status_timer = 1.0
            elif event.type == pygame.MOUSEWHEEL:
                if event.y > 0:
                    zoom = min(MAX_ZOOM, zoom * 1.1)
                elif event.y < 0:
                    zoom = max(MIN_ZOOM, zoom / 1.1)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    left_mouse_down = True
                elif event.button == 3:
                    right_mouse_down = True
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    left_mouse_down = False
                elif event.button == 3:
                    right_mouse_down = False

        keys = pygame.key.get_pressed()
        mods = pygame.key.get_mods()
        has_mod = has_command_mod(mods)
        pan_speed = 800.0 / max(zoom, MIN_ZOOM)
        if keys[pygame.K_LEFT] or (keys[pygame.K_a] and not has_mod):
            pan_x -= pan_speed * dt
        if keys[pygame.K_RIGHT] or (keys[pygame.K_d] and not has_mod):
            pan_x += pan_speed * dt
        if keys[pygame.K_UP] or (keys[pygame.K_w] and not has_mod):
            pan_y -= pan_speed * dt
        if keys[pygame.K_DOWN] or (keys[pygame.K_s] and not has_mod):
            pan_y += pan_speed * dt

        hovered = screen_to_cell(pygame.mouse.get_pos(), draw_x, draw_y, zoom, cols, rows)
        if hovered is not None:
            row, col = hovered
            if left_mouse_down:
                if place_tile(grid, row, col, selected_tile):
                    dirty = True
            elif right_mouse_down:
                if place_tile(grid, row, col, "."):
                    dirty = True

        screen.fill(BACKGROUND_COLOR)
        scaled_world = pygame.transform.smoothscale(world, (scaled_w, scaled_h))
        screen.blit(scaled_world, (draw_x, draw_y))
        draw_grid_overlay(screen, draw_x, draw_y, cols, rows, zoom)

        if hovered is not None:
            hrow, hcol = hovered
            highlight = pygame.Rect(
                draw_x + int(hcol * TILE_SIZE * zoom),
                draw_y + int(hrow * TILE_SIZE * zoom),
                max(2, int(TILE_SIZE * zoom)),
                max(2, int(TILE_SIZE * zoom)),
            )
            pygame.draw.rect(screen, SELECTED_COLOR, highlight, width=max(1, int(2 * zoom)))

        status = "*" if dirty else ""
        info = (
            f"{level_path.name}{status} | Tile {selected_tile} ({TILE_LABELS[selected_tile]}) | "
            "1 empty 2 solid 3 spike 4 start 5 end | LMB paint RMB erase | Cmd/Ctrl+S save | R reload | "
            "+/- zoom | WASD/arrows pan | F fit | Esc quit"
        )
        text = font.render(info, True, TEXT_COLOR)
        screen.blit(text, (12, 10))
        if status_timer > 0.0:
            status_timer = max(0.0, status_timer - dt)
            status = font.render(status_message, True, (134, 239, 172))
            screen.blit(status, (12, 34))

        pygame.display.flip()

    if dirty:
        ensure_required_markers(grid)
        save_grid(level_path, grid)

    pygame.quit()


if __name__ == "__main__":
    main()
