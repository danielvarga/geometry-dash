import math
import pygame

from settings import (
    COYOTE_TIME,
    FORWARD_SPEED,
    GRAVITY,
    JUMP_BUFFER_TIME,
    JUMP_VELOCITY,
    MAX_FALL_SPEED,
    PLAYER_COLOR,
    TILE_SIZE,
)


class Player:
    def __init__(self, x: float, y: float) -> None:
        size = int(TILE_SIZE * 0.85)
        self.rect = pygame.Rect(int(x), int(y), size, size)
        self.velocity_y = 0.0
        self.grounded = False
        self.rotation_degrees = 0.0
        self.coyote_timer = 0.0
        self.jump_buffer_timer = 0.0
        self.hit_head = False

    def reset(self, x: float, y: float) -> None:
        self.rect.topleft = (int(x), int(y))
        self.velocity_y = 0.0
        self.grounded = False
        self.rotation_degrees = 0.0
        self.coyote_timer = 0.0
        self.jump_buffer_timer = 0.0
        self.hit_head = False

    def request_jump(self) -> None:
        self.jump_buffer_timer = JUMP_BUFFER_TIME

    def _try_consume_jump(self) -> None:
        if self.jump_buffer_timer <= 0.0:
            return
        if self.grounded or self.coyote_timer > 0.0:
            self.velocity_y = JUMP_VELOCITY
            self.grounded = False
            self.coyote_timer = 0.0
            self.jump_buffer_timer = 0.0

    def update(self, dt: float, solids: list[pygame.Rect], jump_held: bool) -> None:
        self.hit_head = False

        if jump_held:
            self.request_jump()
        else:
            self.jump_buffer_timer = max(0.0, self.jump_buffer_timer - dt)

        if self.grounded:
            self.coyote_timer = COYOTE_TIME
        else:
            self.coyote_timer = max(0.0, self.coyote_timer - dt)

        self._try_consume_jump()

        self.rect.x += int(FORWARD_SPEED * dt)

        self.velocity_y += GRAVITY * dt
        if self.velocity_y > MAX_FALL_SPEED:
            self.velocity_y = MAX_FALL_SPEED

        self.rect.y += int(self.velocity_y * dt)
        self.grounded = False

        for solid in solids:
            if not self.rect.colliderect(solid):
                continue
            if self.velocity_y > 0:
                self.rect.bottom = solid.top
                self.velocity_y = 0.0
                self.grounded = True
            elif self.velocity_y < 0:
                self.rect.top = solid.bottom
                self.velocity_y = 0.0
                self.hit_head = True

        if self.grounded:
            self.coyote_timer = COYOTE_TIME

        self._try_consume_jump()

        if self.grounded:
            self.rotation_degrees = 0.0
        else:
            self.rotation_degrees = (self.rotation_degrees + 450.0 * dt) % 360.0

    def draw(self, surface: pygame.Surface, camera_x: int) -> None:
        center_x = self.rect.centerx - camera_x
        center_y = self.rect.centery

        base = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        base.fill(PLAYER_COLOR)
        rotated = pygame.transform.rotate(base, self.rotation_degrees)
        draw_rect = rotated.get_rect(center=(center_x, center_y))
        surface.blit(rotated, draw_rect.topleft)

        eye_radius = max(2, self.rect.width // 10)
        eye_offset = self.rect.width // 5
        pupil = (20, 20, 20)
        eye = (245, 245, 245)
        angle = math.radians(self.rotation_degrees)
        for side in (-1, 1):
            ox = side * eye_offset
            rx = ox * math.cos(angle)
            ry = ox * math.sin(angle)
            ex = int(center_x + rx)
            ey = int(center_y + ry)
            pygame.draw.circle(surface, eye, (ex, ey), eye_radius + 1)
            pygame.draw.circle(surface, pupil, (ex, ey), eye_radius)
