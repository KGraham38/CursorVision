import cv2
import  numpy as np
import math

class LookDirection:
    left_iris = [468,469, 470, 471,472]
    right_iris = [473, 474, 475, 476,477]

    left_eye_outside = 33
    left_eye_inside = 133
    right_eye_outside = 263
    right_eye_inside = 362

    left_eye_brow = [70, 63, 105, 66, 107]
    right_eye_brow = [336, 296, 334, 293,300]

    deadzone =.00005
    divide_by_zero = .000001

    def __init__(self):
        self.horizontal_multiplier = 1400.0
        self.vertical_multiplier = 2200.00
        self.cursor_dot_speed = 2.0
        self.show_lines = True

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
        else:
            return int(self.current_look_dot_x), int(self.current_look_dot_y)

    def eye_data(self, landmarks,iris_ids, outside, inside, eyebrow,width, height):
        iris =self.average_point(landmarks, iris_ids, width, height)
        outer = self.average_point(landmarks, [outside], width, height)
        inner = self.average_point(landmarks, [inside], width, height)
        brow = self.average_point(landmarks, eyebrow, width, height)

        eye_mid = ((outer[0] + inner[0]) // 2, (outer[1] + inner[1]) // 2)

        brow_to_eye_len= max(abs(eye_mid[1]-brow[1]), self.divide_by_zero)

        eye_width = max(math.hypot(inner[0] - outer[0], inner[1] - outer[1]), self.divide_by_zero)

        horizontal = (iris[0] - eye_mid[0])/ eye_width
        vertical = (iris[1]-brow[1]) / brow_to_eye_len

        return iris, eye_mid,brow, horizontal ,vertical

    def average_point(self, landmarks, landmarkID, frame_width: int, frame_height: int) -> np.ndarray:

        surrounding_landmark_locations = [self.to_pixels(landmarks[i], frame_width, frame_height) for i in landmarkID]

        return np.mean(np.stack(surrounding_landmark_locations, axis=0), axis=0).astype(int)

    def landmark_features(self, landmarks, width, height):
        left = self.eye_data(landmarks,self.left_iris, self.left_eye_outside,self.left_eye_inside, self.left_eye_brow, width,height)
        right= self.eye_data(landmarks, self.right_iris,self.right_eye_outside, self.right_eye_inside, self.right_eye_brow, width, height)

        left_iris,left_mid, left_brow, left_horizontal, left_vertical = left
        right_iris,right_mid, right_brow, right_horizontal, right_vertical = right

        average_horizontal = (left_horizontal + right_horizontal) / 2.0
        average_vertical = (left_vertical + right_vertical) / 2.0
        centered = ((left_mid[0] + right_mid[0]) // 2, (left_mid[1] + right_mid[1]) // 2)

        return {"left_iris": left_iris, "right_iris": right_iris, "right_mid": right_mid, "left_mid": left_mid,
                "left_brow": left_brow, "right_brow": right_brow, "average_horizontal": average_horizontal,
                "average_vertical": average_vertical, "centered": centered}

    def neutral_eye_center(self, face_landmarks,  frame_shape):
        height,width = frame_shape[:2]
        data = self.landmark_features(face_landmarks, width, height)

        self.neutral_horizontal_pos = data["average_horizontal"]
        self.neutral_vertical_pos = data["average_vertical"]
        self.neutral_set = True


    def clear_neutral_eye_center(self):
        self.neutral_horizontal_pos = None
        self.neutral_vertical_pos = None
        self.neutral_set = False

    def draw(self, frame, face_landmarks):
        height, width = frame.shape[:2]
        data = self.landmark_features(face_landmarks, width, height)

        current_horizontal_pos = data["average_horizontal"]
        current_vertical_pos = data["average_vertical"]
        centered = data["centered"]

        if not self.neutral_set:
            self.neutral_horizontal_pos = current_horizontal_pos
            self.neutral_vertical_pos = current_vertical_pos
            self.neutral_set = True

        look_horizontal = current_horizontal_pos - self.neutral_horizontal_pos
        look_vertical = current_vertical_pos -self.neutral_vertical_pos

        if abs(look_horizontal) < self.deadzone:
            look_horizontal = 0.0
        if abs(look_vertical) < self.deadzone:
            look_vertical = 0.0

        boost_h = look_horizontal* (1.0 + 2.2 * abs(look_horizontal))
        boost_v = look_vertical* (1.0 + 2.2 * abs(look_vertical))

        target_x = int(centered[0] + boost_h * self.horizontal_multiplier)
        target_y = int(centered[1] + boost_v * self.vertical_multiplier)

        target_x = max(0, min(width -1, target_x))
        target_y = max(0, min(height - 1, target_y))

        self.current_look_dot_x = target_x
        self.current_look_dot_y = target_y

        if self.cursor_look_dot_x is None or self.cursor_look_dot_y is None:
            self.cursor_look_dot_x = width / 2.0
            self.cursor_look_dot_y = height /2.0

        line_dx = target_x - centered[0]
        line_dy = target_y - centered[1]
        line_hypotenuse = math.hypot(line_dx, line_dy)

        if line_hypotenuse > self.divide_by_zero:
            direction_x= line_dx / line_hypotenuse
            direction_y= line_dy / line_hypotenuse
            self.cursor_look_dot_x += direction_x * self.cursor_dot_speed
            self.cursor_look_dot_y += direction_y * self.cursor_dot_speed

        self.cursor_look_dot_x = max(0, min(width-1, self.cursor_look_dot_x))
        self.cursor_look_dot_y = max(0, min(height-1, self.cursor_look_dot_y))

        cursor_dot = (int(self.cursor_look_dot_x), int(self.cursor_look_dot_y))

        cv2.circle(frame, data["left_iris"], 5, (0,0,255), -1)
        cv2.circle(frame, data["right_iris"], 5, (0,0,255), -1)

        cv2.circle(frame, data["right_mid"], 5, (255,0,0), -1)
        cv2.circle(frame, data["left_mid"], 5, (255,0,0), -1)

        cv2.circle(frame, data["left_brow"], 5, (255,0,0), -1)
        cv2.circle(frame, data["right_brow"], 5, (255,0,0), -1)

        cv2.circle(frame, centered, 5, (255,255,255), -1)
        cv2.circle(frame, (target_x, target_y), 8, (0,0,255), -1)
        cv2.circle(frame, cursor_dot, 8, (255,255,255), -1)

        if self.show_lines:
            cv2.line(frame,data["left_mid"], data["left_iris"],(0,0,255),2)
            cv2.line(frame,data["right_mid"], data["right_iris"],(0,0,255),2)

            cv2.line(frame,data["right_brow"], data["right_iris"],(255,0,0),2)
            cv2.line(frame,data["left_brow"], data["left_iris"],(255,0,0),2)

            cv2.line(frame,centered, (target_x, target_y),(0,0,255),2)
            cv2.line(frame,centered, cursor_dot,(255,255,255),1)

        status = "Neutral Point Set" if self.neutral_set else "Neutral Point NOT Set"
        cv2.putText(frame, f"Current Est Look Point: ({look_horizontal: .3f},{look_vertical:.3f}) [{status}]",
                    (100,100), cv2.FONT_HERSHEY_DUPLEX, .5, (255,255,255), 1 )







