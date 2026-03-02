from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout
from PyQt5.QtCore import QTimer
from ui.camera_view import CameraView
from ui.menu_buttons_panel import MenuButtonsPanel
from ui.system_status_panel import SystemStatusPanel

class UI_MainMenu(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('CursorVision')
        self.resize(1000, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_menu_layout = QVBoxLayout()
        content_layout = QHBoxLayout()

        # Camera View Panel
        self.camera_view = CameraView()
        # Main Menu Buttons
        self.menu_buttons_panel = MenuButtonsPanel()
        # System Status Panel
        self.system_status_panel = SystemStatusPanel()

        content_layout.addWidget(self.camera_view, 2)
        content_layout.addWidget(self.menu_buttons_panel, 1)
        main_menu_layout.addLayout(content_layout)
        main_menu_layout.addWidget(self.system_status_panel)

        central_widget.setLayout(main_menu_layout)

        # Refresh UI constant view
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_ui)
        self.timer.start(100)

    def update_ui(self):
        self.system_status_panel.update_status()
        self.camera_view.update_status()