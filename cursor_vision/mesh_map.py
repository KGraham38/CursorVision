import cv2

def draw_landmarks(frame_bgr, landmarks):
    height, width = frame_bgr.shape[:2]

    for landmark in landmarks:
        x = int(landmark.x *width)
        y = int(landmark.y *height)

        if 0 <= x < width and 0 <= y < height:
            cv2.circle(frame_bgr, (x, y), 1, (0, 255, 0), -1)