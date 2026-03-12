#Daniyar Alimkhanov

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton
from values_tracking import ValuesTracking

class MenuButtonsPanel(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        self.start_button = QPushButton('Start Cursor Control')
        self.calibrate_button = QPushButton('Calibration Mode')
        self.demo_button = QPushButton('Demo / Test Mode')
        self.settings_button = QPushButton('Settings')

        self.start_button.setMinimumHeight(60)
        self.start_button.clicked.connect(self.start_button_clicked)

        layout.addWidget(self.start_button)
        layout.addWidget(self.calibrate_button)
        layout.addWidget(self.demo_button)
        layout.addWidget(self.settings_button)
        layout.addStretch()

        self.setLayout(layout)

    def start_button_clicked(self):
        ValuesTracking.tracking_active = not ValuesTracking.tracking_active
        if ValuesTracking.tracking_active:
            self.start_button.setText('Stop Cursor Control')
        else:
            self.start_button.setText('Start Cursor Control')