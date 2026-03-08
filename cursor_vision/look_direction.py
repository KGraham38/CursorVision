import cv2

class LookDirection:
    right_iris = [468,469, 470, 471,472]
    left_iris = [473, 474, 475, 476,477]

    left_eye_outside = 33
    left_eye_inside = 133
    right_eye_outside = 263
    right_eye_inside = 262

    left_eyebrow = [70, 63, 105, 66, 107]
    right_eyebrow = [336, 296, 334, 293,300]

    deadzone =.01
    divide_by_zero = .000001

    def __init__(self):
        self.horizontal_multiplier = 1400.0
        self.vertical_multiplier = 2200.00
        self.cursor_dot_speed = 2.0
        self.show_lines = False

        self.current_look_dot_x = None
        self.current_look_dot_y = None

        self.cursor_look_dot_x = None
        self.cursor_look_dot_y = None

        self.neutral_horizontal_pos = None
        self.neutral_vertical_pos = None
        self.neutral_set = False

    def to_pixels(self, landmark, width, height):
        return int(landmark.x * width), int(landmark.y * height)

    #Current pos of the continuous moving cursor
    def get_current_cursor_position(self):
        if self.cursor_look_dot_x is None or self.cursor_look_dot_y is None:
            return None
        return int(self.cursor_look_dot_x), int(self.cursor_look_dot_y)

    #Current point user is projected to be looking at
    def current_look_point(self):
        if self.current_look_dot_x is None or self.current_look_dot_y is None:
            return None
        return int(self.current_look_dot_x), int(self.current_look_dot_y)

    def eye_data(self, landmarks,iris_ids, outside, inside, eyebrow,width, height):
        iris =self.average_point(lanmark, iris_ids, width, height)
        outer = self.average_point(landmark, outer_ids, width, height)
        inner = self.average_point(landmark, inner_ids, width, height)
        brow = self.average_point(landmark, brow_ids, width, height)

        eye_mid = ((outer[0] + inner[0]) // 2), (outer[1] + inner[1]) // 2)

        eye_width = max(math.hypot(inner[0] - outer[0], inner[1] - outer[1]), self.divide_by_zero)


    def average_point(self, landmarks, landmarkID, frame_width: int, frame_height: int) -> np.ndarray:

        surrounding_landmark_locations = [self.to_pixels(landmarks[i], frame_width, frame_height) for i in landmarkID]

        return mean(np.stack(surrounding_landmark_locations, axis=0), axis=0)

    def landmark_features(self):


    def neutral_eye_center(self, face_landmarks,  frame_shape):
        height,width = frame_shape[:2]
        data = self.landmark_features(face_landmarks, width, height)

        self.neutral_horizontal_pos = data[0]
        self.neutral_vertical_pos = data[1]
        self.neutral_set = True



    def clear_neutral_eye_center(self):
        self.neutral_horizontal_pos = None
        self.neutral_vertical_pos = None
        self.neutral_set = False

    def draw(self, frame, face_landmarks) -> bool:


