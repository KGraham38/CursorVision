from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QLabel, QProgressBar)
from values_tracking import ValuesTracking

class SystemStatusPanel(QWidget):
    def __init__(self):
        super().__init__()

        self.fps_label = QLabel('FPS: 0.0')
        self.eye_label = QLabel('Eye Detected: None')
        self.confidence_bar = QProgressBar()
        self.gaze_label = QLabel('Gaze: (0.0, 0.0)')

        layout = QHBoxLayout()
        layout.addWidget(self.fps_label)
        layout.addWidget(self.eye_label)
        layout.addWidget(self.confidence_bar)
        layout.addWidget(self.gaze_label)
        self.setLayout(layout)

    def update_status(self):
        self.fps_label.setText(f"FPS: {ValuesTracking.fps:.0f}")
        self.eye_label.setText(f"Eye Detected: Both"
                               if ValuesTracking.face_found
                               else "Eye Detected: None")
        self.confidence_bar.setValue(int(ValuesTracking.eye_confidence*100))
        self.gaze_label.setText(f"Gaze: {ValuesTracking.gaze_vector[0]:.2f},"
                                f"{ValuesTracking.gaze_vector[1]:.2f})")