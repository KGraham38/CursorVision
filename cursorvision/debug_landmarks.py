#Kody Graham
#1/26/2026
#This file will be for testing different foundations for my FaceMesh landmarks

import time
from pathlib import Path

import cv2
import mediapipe as mp


window_name = "CursorVision - Face Landmarks - Test"
model_path = Path(__file__).resolve().parent.parent / "models" / "face_landmarker.task"

#Draw all landmarks as dots
def draw_landmarks_bgr(frame_bgr, face_landmarks):
    height,width = frame_bgr.shape[:2]
    for landmark in face_landmarks:
        x = int(landmark.x * width)
        y = int(landmark.y * height)
        if 0 <= x < width and 0 <= y < height:
            cv2.circle(frame_bgr, (x, y), 1, (0, 255, 0), -1)

def main():
    if not model_path.exists():
        raise FileNotFoundError(f"Model file not found: {model_path}")

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
        min_tracking_confidence= 0.5 ,
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

            #Mirror so looking left/right is viewed as left/right i think it will be easier than using ML on backwards data and convert it to real intent at the end
            #Start with clear input end with clear output
            frame_bgr = cv2.flip(frame_bgr, 1)

            #BGR to RGB for MediaPipe
            frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format = mp.ImageFormat.SRGB, data=frame_rgb)

            #Timestamp
            timestamp_ms = int((time.time() - start) * 1000)

            result = landmarker.detect_for_video(mp_image, timestamp_ms)

            #Draw landmarks if face found
            if result.face_landmarks:
                draw_landmarks_bgr(frame_bgr, result.face_landmarks[0])
                cv2.putText(frame_bgr, "FACE: FOUND", (10,30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0,255,0),2)
            else:
                cv2.putText(frame_bgr, "FACE: NOT FOUND", (10,30), cv2.FONT_HERSHEY_SIMPLEX,1.0, (0,0,255),2)

            #FPS rate
            now=time.time()
            dt=(now-last_time)
            if dt > 0:
                fps = 0.9 * fps + .1 * (1.0/dt)

            last_time = now
            cv2.putText(frame_bgr, f"FPS: {fps:.1f}", (10,70), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255),2)

            cv2.putText(frame_bgr, f"Press 'ESC' to quit", (10,100), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255),2)

            cv2.imshow(window_name, frame_bgr)

            #ESC
            key = cv2.waitKey(1)
            if key == 27:
                break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
