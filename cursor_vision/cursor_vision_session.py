#Will handle the logic to tie the face landmarks, gaze estimation, and OS cursor movement

from pathlib import Path
import time
from math import hypot

import mesh_map
from values_tracking import ValuesTracking
from look_direction import LookDirection
from cursor_controller import CursorController
from preprocess import build_feature_dict
from tensorflow_model import load_trained_model, predict_target_norm


class CursorVisionSession:
    def __init__(self):
        self.look_direction = LookDirection()
        self.automatic_recalibration = True
        self.cursor_controller = CursorController(smoothing=.5, min_move=2)

        self.gaze_model_path = Path(__file__).resolve().parent.parent / "models" / "gaze_smoother.keras"
        self.tf_model = load_trained_model(self.gaze_model_path)
        self.tf_enabled = False
        self.tf_blend = 0.35

        #Simple TensorFlow confidence gate.
        #Because the model predicts only xy coordinates confidence is just estimated
        #by comparing the TensorFlow point to the raw landmark based point.
        self.tf_confidence_threshold = 0.35
        self.tf_max_distance_ratio = 0.35

        #Only run TensorFlow prediction every 4 frames to reduce lag
        self.tf_frame_interval = 4
        self.tf_frame_counter = 0
        self.last_tf_cursor_point = None

        self.raw_gain_x = 2
        self.raw_gain_y = 1.25

        #Blink settings
        self.min_blink_duration = .1
        self.max_blink_duration = .5
        self.blink_cooldown = .6

        self.left_wink_threshold = .23
        self.right_wink_threshold = .23
        self.eye_open_threshold = .23

        self.left_wink_active = False
        self.left_wink_start_time = 0.0
        self.right_wink_active = False
        self.right_wink_start_time = 0.0
        self.last_click_time = 0.0

        self.recent_left_wink_times = []
        self.recent_right_wink_times = []
        self.triple_blink_timelimit = 1.8

    def amplify_raw_point(self, raw_point, frame_shape):
        if raw_point is None:
            return None

        frame_height, frame_width = frame_shape[:2]
        center_x = frame_width // 2
        center_y = frame_height // 2

        raw_x, raw_y = raw_point

        delta_x = raw_x - center_x
        delta_y = raw_y - center_y

        amplified_x = int(center_x + delta_x * self.raw_gain_x)
        amplified_y = int(center_y + delta_y * self.raw_gain_y)

        amplified_x = max(0, min(frame_width - 1, amplified_x))
        amplified_y = max(0, min(frame_height - 1, amplified_y))

        return amplified_x, amplified_y
    def handle_runtime_stop(self, key):
        if key == 27:
            self.disable_cursor_control()

    def disable_cursor_control(self):
        ValuesTracking.tracking_active = False
        self.cursor_controller.reset()

        self.left_wink_active = False
        self.left_wink_start_time = 0.0
        self.right_wink_active = False
        self.right_wink_start_time = 0.0

        self.recent_left_wink_times = []
        self.recent_right_wink_times = []

    def point_px(self, face_landmarks, index, frame_width, frame_height):
        point = face_landmarks[index]
        return point.x * frame_width, point.y * frame_height

    def distance(self, point1, point2):
        return hypot(point1[0] - point2[0], point1[1] - point2[1])

    def eye_open_ratio(self, face_landmarks, upper_idx, lower_idx, outer_idx, inner_idx, frame_width, frame_height):
        upper = self.point_px(face_landmarks, upper_idx, frame_width, frame_height)
        lower = self.point_px(face_landmarks, lower_idx, frame_width, frame_height)
        outer = self.point_px(face_landmarks, outer_idx, frame_width, frame_height)
        inner = self.point_px(face_landmarks, inner_idx, frame_width, frame_height)

        lid_distance = self.distance(upper, lower)
        eye_width = self.distance(outer, inner)

        if eye_width <= 0:
            return 1

        return lid_distance / eye_width

    def handle_blink_click(self, face_landmarks, frame_width, frame_height):
        left_ratio = self.eye_open_ratio(face_landmarks, 159, 145, 33, 133, frame_width, frame_height)
        right_ratio = self.eye_open_ratio(face_landmarks, 386, 374, 263, 362, frame_width, frame_height)

        now = time.time()

        left_wink = (
                left_ratio < self.left_wink_threshold and
                right_ratio > self.eye_open_threshold
        )

        right_wink = (
                right_ratio < self.right_wink_threshold and
                left_ratio > self.eye_open_threshold
        )

        both_closed = (
                left_ratio < self.left_wink_threshold and
                right_ratio < self.right_wink_threshold
        )

        #Ignore both eyes closed
        if both_closed:
            self.left_wink_active = False
            self.right_wink_active = False
            return

        #LEFT EYE -> LEFT CLICK /TRIPLE LEFT WINK DISABLE
        if left_wink and not self.left_wink_active:
            self.left_wink_active = True
            self.left_wink_start_time = now
            return

        if not left_wink and self.left_wink_active:
            self.left_wink_active = False
            wink_duration = now - self.left_wink_start_time

            if self.min_blink_duration <= wink_duration <= self.max_blink_duration:
                self.recent_left_wink_times = [
                    blink_time for blink_time in self.recent_left_wink_times
                    if now - blink_time <= self.triple_blink_timelimit
                ]
                self.recent_left_wink_times.append(now)

                if len(self.recent_left_wink_times) >= 3:
                    self.disable_cursor_control()
                    return

                if now - self.last_click_time >= self.blink_cooldown:
                    self.cursor_controller.left_click()
                    self.last_click_time = now
                    return

        #RIGHT EYE -> RIGHT CLICK / TRIPLE RIGHT WINK DISABLE
        if right_wink and not self.right_wink_active:
            self.right_wink_active = True
            self.right_wink_start_time = now
            return

        if not right_wink and self.right_wink_active:
            self.right_wink_active = False
            wink_duration = now - self.right_wink_start_time

            if self.min_blink_duration <= wink_duration <= self.max_blink_duration:
                self.recent_right_wink_times = [
                    blink_time for blink_time in self.recent_right_wink_times
                    if now - blink_time <= self.triple_blink_timelimit
                ]
                self.recent_right_wink_times.append(now)

                if len(self.recent_right_wink_times) >= 3:
                    self.disable_cursor_control()
                    return

                if now - self.last_click_time >= self.blink_cooldown:
                    self.cursor_controller.right_click()
                    self.last_click_time = now
                    return

    def reset_tracking(self):
        self.look_direction.clear_neutral_eye_center()
        self.look_direction.current_look_dot_x = None
        self.look_direction.current_look_dot_y = None
        self.look_direction.cursor_look_dot_x = None
        self.look_direction.cursor_look_dot_y = None
        self.cursor_controller.reset()
        ValuesTracking.gaze_vector = (0.0, 0.0)
        ValuesTracking.eye_confidence = 0.0

        self.left_wink_active = False
        self.left_wink_start_time = 0.0
        self.right_wink_active = False
        self.right_wink_start_time = 0.0
        self.last_click_time = 0.0

        self.recent_left_wink_times = []
        self.recent_right_wink_times = []

    def handle_no_face(self):
        ValuesTracking.gaze_vector = (0.0, 0.0)
        ValuesTracking.eye_confidence = 0.0

        self.left_wink_active = False
        self.right_wink_active = False
        self.recent_left_wink_times = []
        self.recent_right_wink_times = []

    def blend_points(self, raw_point, tf_point):
        if raw_point is None:
            return tf_point
        if tf_point is None:
            return raw_point

        raw_x, raw_y = raw_point
        tf_x, tf_y = tf_point

        final_x = int(raw_x + (tf_x - raw_x) * self.tf_blend)
        final_y = int(raw_y + (tf_y - raw_y) * self.tf_blend)
        return final_x, final_y

    def tf_prediction_confidence(self, raw_point, tf_point, frame_shape):
        if raw_point is None or tf_point is None:
            return 0.0

        frame_height, frame_width = frame_shape[:2]
        frame_diagonal = hypot(frame_width, frame_height)

        if frame_diagonal <= 0:
            return 0.0

        raw_x, raw_y = raw_point
        tf_x, tf_y = tf_point

        prediction_distance = hypot(tf_x - raw_x, tf_y - raw_y)
        max_allowed_distance = frame_diagonal * self.tf_max_distance_ratio

        if max_allowed_distance <= 0:
            return 0.0

        confidence = 1.0 - (prediction_distance / max_allowed_distance)
        confidence = max(0.0, min(1.0, confidence))

        return confidence

    def should_use_tf_prediction(self, raw_point, tf_point, frame_shape):
        confidence = self.tf_prediction_confidence(raw_point, tf_point, frame_shape)
        return confidence >= self.tf_confidence_threshold

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
            raw_cursor_point = self.look_direction.get_current_cursor_position()
            raw_cursor_point = self.amplify_raw_point(raw_cursor_point, frame_bgr.shape)
            final_cursor_point = raw_cursor_point

            if self.tf_enabled and self.tf_model is not None:
                feature_dict = build_feature_dict(self.look_direction, face_landmarks, frame_bgr.shape)
                tf_prediction = predict_target_norm(self.tf_model, feature_dict)

                if self.tf_enabled and self.tf_model is not None:
                    feature_dict = build_feature_dict(self.look_direction, face_landmarks, frame_bgr.shape)
                    tf_prediction = predict_target_norm(self.tf_model, feature_dict)

                    if self.tf_enabled and self.tf_model is not None:
                        self.tf_frame_counter += 1

                        if self.tf_frame_counter >= self.tf_frame_interval:
                            self.tf_frame_counter = 0

                            feature_dict = build_feature_dict(self.look_direction, face_landmarks, frame_bgr.shape)
                            tf_prediction = predict_target_norm(self.tf_model, feature_dict)

                            if tf_prediction is not None:
                                pred_x_norm, pred_y_norm = tf_prediction

                                tf_frame_x = int(pred_x_norm * max(frame_width - 1, 1))
                                tf_frame_y = int(pred_y_norm * max(frame_height - 1, 1))

                                tf_frame_x = max(0, min(frame_width - 1, tf_frame_x))
                                tf_frame_y = max(0, min(frame_height - 1, tf_frame_y))

                                self.last_tf_cursor_point = (tf_frame_x, tf_frame_y)

                        if self.last_tf_cursor_point is not None:
                            if self.should_use_tf_prediction(raw_cursor_point, self.last_tf_cursor_point,
                                                             frame_bgr.shape):
                                final_cursor_point = self.blend_points(raw_cursor_point, self.last_tf_cursor_point)

            self.cursor_controller.move_to_frame_point(final_cursor_point, frame_bgr.shape)
            self.handle_blink_click(face_landmarks, frame_width, frame_height)