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
        self.dot_speed = 18
        self.show_proj_lines = False
        self.dot_radius = 20

    def to_pixels(self, landmark, frame_width: int, frame_height: int) -> np.ndarray:
        return np.array([landmark.x, frame_width, landmark.y * frame_height], dtype=np.float32)

    def get_current_cursor_position:
    def current_look_point(self):
    def eye_data(self):

    def eye_center(self, landmarks, landmarkID, frame_width: int, frame_height: int) -> np.ndarray:

        surrounding_landmark_locations = [self.to_pixels(landmarks[i], frame_width, frame_height) for i in landmarkID]

        return mean(np.stack(surrounding_landmark_locations, axis=0), axis=0)

    def landmark_features(self):

    def neutral_eye_center(self, landmarks, landmarkID, frame_width: int, frame_height: int) -> np.ndarray:

    def clear_neutral_eye_center(self):


    def draw(self, frame, face_landmarks) -> bool:


