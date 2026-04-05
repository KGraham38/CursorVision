#Will handle OS cursor control pre my tensorflow system

import ctypes
import platform


class CursorController:
    def __init__(self, smoothing = .5, min_move = 2):
        self.smoothing = float(smoothing)
        self.min_move = int(min_move)
        self.last_screen_x = None
        self.last_screen_y = None
        self.is_windows = platform.system().lower().startswith('win')
        self.user32 = ctypes.windll.user32 if self.is_windows else None

    def left_click(self):
        if self.is_windows:
            self.user32.mouse_event(0x0002,0,0,0,0)
            self.user32.mouse_event(0x0004,0,0,0,0)

    def reset(self):
        self.last_screen_x = None
        self.last_screen_y = None

    def get_screen_size(self):
        if not self.is_windows:
            return 1920, 1080
        return self.user32.GetSystemMetrics(0), self.user32.GetSystemMetrics(1)

    def frame_point_to_screen(self, frame_point, frame_shape):
        if frame_point is None or frame_shape is None:
            return None

        frame_height, frame_width = frame_shape[:2]
        if frame_width <= 1 or frame_height <= 1:
            return None

        frame_x, frame_y = frame_point
        screen_width, screen_height = self.get_screen_size()

        screen_x = int((frame_x / float(frame_width-1)) * (screen_width-1))
        screen_y = int((frame_y / float(frame_height-1)) * (screen_height-1))

        screen_x = max(0, min(screen_width-1, screen_x))
        screen_y = max(0, min(screen_height-1, screen_y))
        return screen_x, screen_y

    def move_to_frame_point(self, frame_point, frame_shape):
        target = self.frame_point_to_screen(frame_point, frame_shape)

        if target is None:
            return None

        target_x, target_y = target

        if self.last_screen_x is None or self.last_screen_y is None:
            smoothed_x = target_x
            smoothed_y = target_y
        else:
            smoothed_x = int(self.last_screen_x + (target_x - self.last_screen_x) * self.smoothing)
            smoothed_y = int(self.last_screen_y + (target_y - self.last_screen_y) * self.smoothing)

        if self.last_screen_x is not None or self.last_screen_y is not None:
            delta_x = abs(smoothed_x - self.last_screen_x)
            delta_y = abs(smoothed_y - self.last_screen_y)

            if delta_x < self.min_move and delta_y < self.min_move:
                return self.last_screen_x, self.last_screen_y

        if self.is_windows:
            self.user32.SetCursorPos(smoothed_x, smoothed_y)

        self.last_screen_x = smoothed_x
        self.last_screen_y = smoothed_y
        return smoothed_x, smoothed_y