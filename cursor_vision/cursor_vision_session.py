#Will handle the logic to tie the face landmarks, gaze estimation, and OS cursor movement

from values_tracking import ValuesTracking
from look_direction import LookDirection
from cursor_controller import CursorController
import mesh_map
import time
from math import hypot


class CursorVisionSession:
    def __init__(self):
        self.look_direction = LookDirection()
        self.automatic_recalibration = True
        self.cursor_controller = CursorController(smoothing= .5, min_move =2)


        #Blink to click
        self.blink_threshold = .2
        self.min_blink_duration = .1
        self.max_blink_duration = .5
        self.blink_cooldown = .6

        self.blink_active = False
        self.blink_start_time = 0.0
        self.last_click_time = 0.0
        self.recent_blink_times=[]
        self.triple_blink_timelimit = 1.8

    def handle_runtime_stop(self, key):
        if key == 27:
            self.disable_cursor_control()

    def disable_cursor_control(self):
        ValuesTracking.tracking_active = False
        self.cursor_controller.reset()
        self.blink_active = False
        self.recent_blink_times = []

    def point_px(self,face_landmarks, index, frame_width, frame_height):
        point = face_landmarks[index]
        return point.x * frame_width, point.y * frame_height

    def distance(self, point1, point2):
        return hypot(point1[0] - point2[0], point1[1] - point2[1])

    def eye_open_ratio(self, face_landmarks, upper_idx,lower_idx, outer_idx, inner_idx, frame_width, frame_height):
        upper = self.point_px(face_landmarks, upper_idx, frame_width, frame_height)
        lower = self.point_px(face_landmarks, lower_idx, frame_width, frame_height)
        outer = self.point_px(face_landmarks, outer_idx, frame_width, frame_height)
        inner = self.point_px(face_landmarks, inner_idx, frame_width, frame_height)

        lid_distance = self.distance(upper, lower)
        eye_width = self.distance(outer, inner)

        if eye_width <= 0:
            return 1

        return lid_distance / eye_width

    def handle_blink_click(self,face_landmarks, frame_width, frame_height):
        left_ratio = self.eye_open_ratio(face_landmarks, 159,145,33,133,frame_width, frame_height)
        right_ratio = self.eye_open_ratio(face_landmarks, 386,374,263,362,frame_width, frame_height)

        average_ratio = (left_ratio + right_ratio) / 2
        eyes_closed = average_ratio < self.blink_threshold
        now = time.time()

        if eyes_closed and not self.blink_active:
            self.blink_active = True
            self.blink_start_time = now
            return

        if not eyes_closed and self.blink_active:
            self.blink_active = False
            blink_duration = now - self.blink_start_time

            if self.min_blink_duration <= blink_duration <= self.max_blink_duration:
                self.recent_blink_times = [blink_time for blink_time in self.recent_blink_times if now-blink_time <= self.triple_blink_timelimit]
                self.recent_blink_times.append(now)

                if len(self.recent_blink_times) >= 3:
                    self.disable_cursor_control()
                    return

                if now - self.last_click_time >= self.blink_cooldown:
                    self.cursor_controller.left_click()
                    self.last_click_time = now

    def reset_tracking(self):
        self.look_direction.clear_neutral_eye_center()
        self.look_direction.current_look_dot_x = None
        self.look_direction.current_look_dot_y = None
        self.look_direction.cursor_look_dot_x = None
        self.look_direction.cursor_look_dot_y = None
        self.cursor_controller.reset()
        ValuesTracking.gaze_vector = (0.0, 0.0)
        ValuesTracking.eye_confidence = 0.0


        self.blink_active = False
        self.blink_start_time = 0.0
        self.last_click_time = 0.0
        self.recent_blink_times = []

    def handle_no_face(self):
        ValuesTracking.gaze_vector = (0.0, 0.0)
        ValuesTracking.eye_confidence = 0.0
        self.blink_active = False
        self.recent_blink_times = []

    def process_face_landmarks(self, frame_bgr, face_landmarks):
        frame_height, frame_width = frame_bgr.shape[:2]

        if self.automatic_recalibration and not self.look_direction.neutral_set:
            self.look_direction.neutral_eye_center(face_landmarks, frame_bgr.shape)

        features = self.look_direction.landmark_features(face_landmarks, frame_width, frame_height)

        if self.look_direction.neutral_horizontal_pos is None:
            look_horizontal = 0.0
        else:
            look_horizontal = features["average_horizontal"] - self.look_direction.neutral_horizontal_pos

        if self.look_direction.neutral_vertical_pos is None:
            look_vertical = 0.0
        else:
            look_vertical = features["average_vertical"] - self.look_direction.neutral_vertical_pos

        ValuesTracking.gaze_vector = (float(look_horizontal), float(look_vertical))
        ValuesTracking.eye_confidence = 1

        mesh_map.draw_landmarks(frame_bgr, face_landmarks)
        self.look_direction.draw(frame_bgr, face_landmarks)

        if ValuesTracking.tracking_active:
            cursor_point = self.look_direction.get_current_cursor_position()
            self.cursor_controller.move_to_frame_point(cursor_point, frame_bgr.shape)
            self.handle_blink_click(face_landmarks, frame_width, frame_height)