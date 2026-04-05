#Daniyar Alimkhanov
from PyQt5.QtWidgets import (QFrame, QLabel, QVBoxLayout)
from PyQt5.QtCore import Qt, QTimer
from values_tracking import ValuesTracking
from PyQt5.QtGui import QImage, QPixmap

import cv2
import time

import mediapipe as mp
from pathlib import Path
from cursor_vision_session import CursorVisionSession

model_path = Path(__file__).resolve().parent.parent.parent / "models" / "face_landmarker.task"
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
        self.cap = None
        self.landmarker = None
        self.cursor_session = CursorVisionSession()

        #Time
        self.start = time.time()
        self.last_time = self.start
        self.fps = 0.0

        #self.prev_time = time.time()

        # TIMER (same as in debug_landmarks)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.start_camera()
        self.timer.start(30)

    def create_landmarker(self):
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
            output_facial_transformation_matrixes=False,
        )

        return face_landmarker.create_from_options(options)

    def update_frame(self):
        if self.cap is None or self.landmarker is None:
            return

        ok, frame_bgr = self.cap.read()
        if not ok:
            return

        frame_bgr = cv2.flip(frame_bgr, 1)
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)

        timestamp_ms = int((time.time() - self.start) * 1000)
        result = self.landmarker.detect_for_video(mp_image, timestamp_ms)

        if result.face_landmarks:
            ValuesTracking.face_found = True
            self.cursor_session.process_face_landmarks(frame_bgr, result.face_landmarks[0])
        else:
            ValuesTracking.face_found = False
            self.cursor_session.handle_no_face()

        now = time.time()
        dt = now - self.last_time
        if dt > 0:
            self.fps = 0.9 * self.fps + 0.1 * (1.0 / dt)

        self.last_time = now
        ValuesTracking.fps = self.fps

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

    def set_tracking_active(self, active):
        ValuesTracking.tracking_active = bool(active)
        if active:
            self.cursor_session.reset_tracking()
        else:
            self.cursor_session.cursor_controller.reset()

    def stop_camera(self):
        self.timer.stop()
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        if self.landmarker is not None:
            self.landmarker.close()
            self.landmarker = None

    def start_camera(self):
        if self.cap is None:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                raise Exception("Could not open camera")

        if self.landmarker is None:
            self.landmarker = self.create_landmarker()

        self.start = time.time()
        self.last_time = self.start

        if not self.timer.isActive():
            self.timer.start(30)