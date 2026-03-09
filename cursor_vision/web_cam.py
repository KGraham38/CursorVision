import cv2
import mediapipe as mp

import mesh_map as mesh_map
from pathlib import Path
import time


window_name = "CursorVision - Face Landmarks - Test"
model_path = Path(__file__).resolve().parent.parent / "models" / "face_landmarker.task"

class Webcam():
    def __init__(self):

        if not model_path.exists():
            raise FileNotFoundError(f"Model file not found: {model_path}")

        #MediaPipe uses Tasks instead of "mp.solutions" like the older examples I had been looking at
        self.base_options = mp.tasks.BaseOptions
        self.face_landmarker = mp.tasks.vision.FaceLandmarker
        self.face_landmarker_options = mp.tasks.vision.FaceLandmarkerOptions
        self.vision_running_mode = mp.tasks.vision.RunningMode

        self.options = self.face_landmarker_options(
            base_options=self.base_options(model_asset_path=str(model_path)),
            running_mode=self.vision_running_mode.VIDEO,
            num_faces=1,
            min_face_detection_confidence=0.5,
            min_face_presence_confidence=0.5,
            min_tracking_confidence=0.5,
            output_face_blendshapes=False,
            output_facial_transformation_matrixes=False, )

    def run(self, helper_class=None):

        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            raise Exception("Could not open camera")

        #Craete window
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

        start = time.time()
        last_time = start
        fps = 0.0

        with self.face_landmarker.create_from_options(self.options) as landmarker:
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
                    face_landmarks = result.face_landmarks[0]
                    mesh_map.draw_landmarks(frame_bgr, result.face_landmarks[0])
                    cv2.putText(frame_bgr, "FACE: FOUND", (10,30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0,255,0),2)

                    if helper_class is not None:
                        helper_class.draw(frame_bgr, face_landmarks)
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
    Webcam().run()
