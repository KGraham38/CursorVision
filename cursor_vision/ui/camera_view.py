#Daniyar Alimkhanov
from PyQt5.QtWidgets import (QFrame, QLabel, QVBoxLayout)
from PyQt5.QtCore import Qt, QTimer
from values_tracking import ValuesTracking
from PyQt5.QtGui import QImage, QPixmap

import cv2
import time

import mediapipe as mp
from pathlib import Path

model_path = Path(__file__).resolve().parent.parent / "models" / "face_landmarker.task"
if not model_path.exists():
    raise FileNotFoundError(f"Model file not found: {model_path}")

def draw_landmarks_bgr(frame_bgr, face_landmarks):
    height,width = frame_bgr.shape[:2]
    for landmark in face_landmarks:
        x = int(landmark.x * width)
        y = int(landmark.y * height)
        if 0 <= x < width and 0 <= y < height:
            cv2.circle(frame_bgr, (x, y), 1, (0, 255, 0), -1)

class CameraView(QFrame):
    def __init__(self):
        super().__init__()

        self.setFrameShape(QFrame.StyledPanel)

        #AI part
        self.setStyleSheet("""
                QFrame {
                    background-color: #101418;
                    border: 2px solid #2d7dff;
                    border-radius: 12px;
                }
                """)

        self.title=QLabel("Live Camera Feed")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet("font-size: 20px; font-weight: bold;")

        self.status_label = QLabel("FACE: NOT FOUND")
        self.status_label.setAlignment(Qt.AlignCenter)

        self.fps_label = QLabel("FPS: 0.0")
        self.fps_label.setAlignment(Qt.AlignCenter)

        self.camera_placeholder = QLabel("Camera Preview Placeholder")
        self.camera_placeholder.setAlignment(Qt.AlignCenter)

        #AI part
        self.camera_placeholder.setStyleSheet("""
                QLabel {
                    background-color: #222;
                    color: white;
                    border-radius: 8px;
                    min-height: 350px;
                }
                """)

        layout = QVBoxLayout()
        layout.addWidget(self.title)
        layout.addWidget(self.status_label)
        layout.addWidget(self.fps_label)
        layout.addWidget(self.camera_placeholder)

        self.setLayout(layout)

        #CAMERA ADDITION
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            raise Exception("Could not open camera")



        # MediaPipe uses Tasks instead of "mp.solutions" like the older examples I had been looking at
        base_options = mp.tasks.BaseOptions
        face_landmarker = mp.tasks.vision.FaceLandmarker
        face_landmarker_options = mp.tasks.vision.FaceLandmarkerOptions
        vision_running_mode = mp.tasks.vision.RunningMode

        options = face_landmarker_options(
            base_options=base_options(model_asset_path=str(model_path)),
            running_mode=vision_running_mode.VIDEO,
            num_faces=1,
            min_face_detection_confidence=0.5,
            min_face_presence_confidence=0.5,
            min_tracking_confidence=0.5,
            output_face_blendshapes=False,
            output_facial_transformation_matrixes=False, )

        self.landmarker = face_landmarker.create_from_options(options)

        #Time
        self.start = time.time()
        self.last_time = self.start
        self.fps = 0.0

        #self.prev_time = time.time()

        # TIMER (same as in debug_landmarks)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

    def update_frame(self):

        ok, frame_bgr = self.cap.read()
        if not ok:
            return

        # Flip for mirror view
        frame_bgr = cv2.flip(frame_bgr, 1)
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)

        timestamp_ms = int((time.time() - self.start) * 1000)

        result = self.landmarker.detect_for_video(mp_image, timestamp_ms)

        # Draw landmarks if face found
        if result.face_landmarks:
            draw_landmarks_bgr(frame_bgr, result.face_landmarks[0])
            ValuesTracking.face_found = True
        else:
            ValuesTracking.face_found = False

        # FPS rate
        now = time.time()
        dt = (now - self.last_time)
        if dt > 0:
            self.fps = 0.9 * self.fps + .1 * (1.0 / dt)

        self.last_time = now
        ValuesTracking.fps = self.fps

        #removed so it won't be shown on the camera
        #cv2.putText(frame_bgr, f"FPS: {self.fps:.1f}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

        # Convert frame to Qt format
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)

        h, w, ch = frame_rgb.shape
        bytes_per_line = ch * w

        qt_image = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)

        pixmap = QPixmap.fromImage(qt_image)

        self.camera_placeholder.setPixmap(
            pixmap.scaled(
                self.camera_placeholder.width(),
                self.camera_placeholder.height(),
                Qt.KeepAspectRatio
            )
        )

    def update_status(self):
        self.status_label.setText("FACE: FOUND" if ValuesTracking.face_found
                                  else "FACE: NOT FOUND")
        self.fps_label.setText(f"FPS: {ValuesTracking.fps:.1f}")