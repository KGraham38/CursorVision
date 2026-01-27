#Kody Graham
#1/26/2026
#This file will be the foundation for my FaceMesh landmarks
import time
from pathlib import Path

import cv2
import mediapipe as mp

window_name = "CursorVision - Face Landmarks - Test"
model_path = Path(__file__).parent / "models" / "face_landmarker.task"

#Draw all landmarks as dots
def draw_landmarks_bgr(frame_bgr, face_landmarks):
    h,w,_ = frame_bgr.shape[:2]
    for landmark in face_landmarks:
        x = int(landmark.x * w)
        y = int(landmark.y * h)
        if 0 <= x < w and 0 <= y < h:
            cv2.circle(frame_bgr, (x, y), 1, (255, 0, 0), -1)

def main():
    if not model_path.exists():
        raise FileNotFoundError("Model not found at : " + str(model_path))

    #MediaPipe uses Tasks instead of "mp.solutions" like the older examples I had been looking at
    base_options = mp.tasks.BaseOptions
    face_landmarker = mp.tasks.vision.FaceLandmarker
    face_landmarker_options = mp.tasks.vision.FaceLandmarkerOptions
    vision_running_mode = mp.tasks.vision.RunningMode

    options = face_landmarker_options(
        base_options = base_options(model_asset_path = str(model_path)),
        running_mode = vision_running_mode.VIDEO,
        num_faces = 1,
        min_face_detection_confidence = 0.5,
        min_face_presence_confidence = 0.5,
        output_face_blendshapes = False,
        output_facial_transformation_matrixes = False,)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise Exception("Could not open camera")

    #Craete window
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    start = time.time()
    last_time = start
    fps = 0.0

    with face_landmarker.create_from_options(options) as landmarker:
        while True:
            ok, frame_bgr = cap.read()
            if not ok:
                break

            #BGR to RGB for MediaPipe
            fran_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB0)
