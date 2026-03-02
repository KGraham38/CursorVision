from PyQt5.QtWidgets import (QFrame, QLabel, QVBoxLayout)
from PyQt5.QtCore import Qt
from values_tracking import ValuesTracking

class CameraView(QFrame):
    def __init__(self):
        super().__init__()
        self.setFrameShape(QFrame.StyledPanel)

        self.title=QLabel("Live Camera Feed")
        self.title.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.status_label = QLabel("FACE: NOT FOUND")
        self.fps_label = QLabel("FPS: 0.0")

        self.camera_placeholder = QLabel("Camera Preview Placeholder")
        self.camera_placeholder.setStyleSheet("background-color: #222; "
                                              "color: White;")
        self.camera_placeholder.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout()
        layout.addWidget(self.title)
        layout.addWidget(self.status_label)
        layout.addWidget(self.fps_label)
        layout.addWidget(self.camera_placeholder)

        self.setLayout(layout)

    def update_status(self):
        self.status_label.setText("FACE: FOUND" if ValuesTracking.face_found
                                  else "FACE: NOT FOUND")
        self.fps_label.setText(f"FPS: {ValuesTracking.fps:.1f}")