import cv2

class LookDirection:
    right_iris = [469, 470, 471,472]
    left_iris = [474, 475, 476,477]

    def __init__(self):
        self.dot_speed = 18
        self.show_proj_lines = False
        self.dot_radius = 20

    def to_pixels(self, landmark, frame_width: int, frame_height: int) -> np.ndarray:
        return np.array([landmark.x, frame_width, landmark.y * frame_height], dtype=np.float32)

    def eye_center(self, landmarks, landmarkID, frame_width: int, frame_height: int) -> np.ndarray:

        surrounding_landmark_locations = [self.to_pixels(landmarks[i], frame_width, frame_height) for i in landmarkID]

        return mean(np.stack(surrounding_landmark_locations, axis=0), axis=0)

    def draw(self, frame, face_landmarks) -> bool:


