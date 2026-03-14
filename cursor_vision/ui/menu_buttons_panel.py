#Daniyar Alimkhanov

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton
from values_tracking import ValuesTracking
from demo_mode import DemoMode
from ui.settings_menu import SettingsWindow

class MenuButtonsPanel(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        self.start_button = QPushButton('Start Cursor Control')
        self.calibrate_button = QPushButton('Calibration Mode')
        self.demo_button = QPushButton('Demo / Test Mode')
        self.settings_button = QPushButton('Settings')
        self.settings_button.clicked.connect(self.settings_button_clicked)

        self.start_button.setMinimumHeight(60)
        self.start_button.clicked.connect(self.start_button_clicked)
        self.demo_button.clicked.connect(self.demo_button_clicked)
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

    def demo_button_clicked(self):

        main_window = self.window()
        main_window.camera_view.stop_camera()
        self.demo_mode = DemoMode()
        self.demo_mode.run()
        main_window.camera_view.start_camera()

    def settings_button_clicked(self):
        window = SettingsWindow(parent=self.window())
        window.exec_()

