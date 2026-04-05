#Will handle the logic to tie the face landmarks, gaze estimation, and OS cursor movement
from pyexpat import features

from values_tracking import ValuesTracking
from look_direction import LookDirection
from cursor_controller import CursorController
import mesh_map


class CursorVisionSession:
    def __init__(self):
        self.look_direction = LookDirection()
        self.automatic_recalibration = True

    def reset_tracking(self):
        self.look_direction.clear_neutral_eye_center()
        self.look_direction.current_look_dot_x = None
        self.look_direction.current_look_dot_y = None
        self.look_direction.cursor_look_dot_x = None
        self.look_direction.cursor_look_dot_y = None
        self.cursor_controller.reset()
        ValuesTracking.gaze_vector = (0.0, 0.0)
        ValuesTracking.eye_confidence = 0.0

    def handle_no_face(self):
        ValuesTracking.gaze_vector = (0.0, 0.0)
        ValuesTracking.eye_confidence = 0.0

    def process_face_landmarks(self, frame_bgr, face_landmarks):
        frame_height, frame_width, _ = frame_bgr.shape[:2]

        if self.automatic_recalibration and not self.look_direction.neutral_set:
            self.look_direction.neutral_eye_center(face_landmarks, frame_bgr.shape)

        features = self.look_direction.landmark_features(face_landmarks, frame_width, frame_height)

        if self.look_direction.neutral_vertical_pos is None:
            look_horizontal = 0.0
        else:
            look_direction = features["average_horizontal"] - self.look_direction.neutral_horizontal_pos

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
            self.cursor_controller. move_to_fram_point(cursor_point, frame_bgr.shape)