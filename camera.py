from settings import FORWARD_SPEED, SCREEN_WIDTH


def compute_camera_x(player_x: int, level_width_px: int) -> int:
    look_ahead = int(FORWARD_SPEED * 0.6)
    target_x = player_x - SCREEN_WIDTH // 3 + look_ahead
    max_camera = max(0, level_width_px - SCREEN_WIDTH)
    if target_x < 0:
        return 0
    if target_x > max_camera:
        return max_camera
    return target_x
