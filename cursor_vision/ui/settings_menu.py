# Seth Wojcik
# Settings menu for CursorVision


import json
from pathlib import Path
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QLabel, QSlider, QCheckBox, QPushButton,
    QGroupBox, QLineEdit, QListWidget, QMessageBox
)
from PyQt5.QtCore import Qt


# Directory for saved user profiles and file used to track the active profile
PROFILES_DIR   = Path(__file__).resolve().parent.parent / "profiles"
ACTIVE_FILE    = Path(__file__).resolve().parent.parent / "active_profile.txt"


# Stylesheet matching the main menu format and theme
SETTINGS_STYLE = """
    QDialog {
        background-color: #2b2f36;
    }
    QWidget {
        background-color: #2b2f36;
        color: white;
        font-family: Segoe UI;
        font-size: 13px;
    }
    QTabWidget::pane {
        border: 1px solid #2d7dff;
        border-radius: 8px;
        background-color: #2b2f36;
    }
    QTabBar {
        alignment: left;
    }
    QTabBar::tab {
        background-color: #1c2026;
        color: white;
        font-family: Segoe UI;
        font-size: 13px;
        padding: 10px 16px;
        border-top-left-radius: 6px;
        border-top-right-radius: 6px;
        margin-right: 2px;
        min-width: 100px;
    }
    QTabBar::tab:selected {
        background-color: #2d7dff;
    }
    QTabBar::tab:hover {
        background-color: #3a4250;
    }
    QGroupBox {
        border: 1px solid #3a4250;
        border-radius: 8px;
        margin-top: 14px;
        padding: 12px;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 0 6px;
        color: #2d7dff;
        font-weight: bold;
        font-size: 16px;
    }
    QListWidget {
        background-color: #1c2026;
        color: white;
        border: 1px solid #3a4250;
        border-radius: 6px;
    }
    QListWidget::item:selected {
        background-color: #2d7dff;
        border-radius: 4px;
    }
    QLineEdit {
        background-color: #1c2026;
        color: white;
        border: 1px solid #3a4250;
        border-radius: 6px;
        padding: 4px 8px;
        min-height: 28px;
    }
    QCheckBox {
        color: white;
        spacing: 8px;
    }
    QCheckBox::indicator {
        width: 18px;
        height: 18px;
        border-radius: 4px;
        border: 2px solid #2d7dff;
        background-color: #1c2026;
    }
    QCheckBox::indicator:checked {
        background-color: #2d7dff;
    }
    QPushButton {
        background-color: #2d7dff;
        color: white;
        border-radius: 20px;
        padding: 10px;
        font-size: 14px;
        min-height: 36px;
    }
    QPushButton:hover {
        background-color: #4090ff;
    }
    QLabel {
        color: white;
        background-color: transparent;
    }
"""


# Creates a labeled horizontal slider with a live value display.
def _slider_row(label, minimum, maximum, default):
    row = QWidget()
    row.setStyleSheet("background-color: transparent;")
    layout = QHBoxLayout(row)
    layout.setContentsMargins(0, 0, 0, 0)
    lbl = QLabel(label)
    lbl.setMinimumWidth(190)
    slider = QSlider(Qt.Horizontal)
    slider.setMinimum(minimum)
    slider.setMaximum(maximum)
    slider.setValue(default)
    slider.setMinimumWidth(200)
    val_lbl = QLabel(str(default))
    # Updates the label in realtime when it moves
    slider.valueChanged.connect(lambda v: val_lbl.setText(str(v)))
    layout.addWidget(lbl)
    layout.addWidget(slider)
    layout.addWidget(val_lbl)
    return row, slider


# Creates a spinbox to control the values by increments 
def _spinbox_row(label, minimum, maximum, default, suffix=""):
    row = QWidget()
    row.setStyleSheet("background-color: transparent;")
    layout = QHBoxLayout(row)
    layout.setContentsMargins(0, 0, 0, 0)
    lbl = QLabel(label)
    lbl.setMinimumWidth(190)

    val = [default]
    val_lbl = QLabel(f"{default}{suffix}")
    val_lbl.setStyleSheet(
        "background-color: #1c2026; color: white; border: 1px solid #2d7dff;"
        "border-radius: 6px; padding: 4px 10px; min-width: 60px;"
    )
    val_lbl.setAlignment(Qt.AlignCenter)

    down_btn = QPushButton("▼")
    up_btn   = QPushButton("▲")
    for btn in (down_btn, up_btn):
        btn.setFixedSize(32, 32)
        btn.setStyleSheet(
            "QPushButton { background-color: #2d7dff; color: white; border-radius: 6px;"
            "font-size: 12px; padding: 0; min-height: 0; }"
            "QPushButton:hover { background-color: #4090ff; }"
        )

    def update(delta):
        val[0] = max(minimum, min(maximum, val[0] + delta))
        val_lbl.setText(f"{val[0]}{suffix}")

    down_btn.clicked.connect(lambda: update(-100))
    up_btn.clicked.connect(lambda:   update( 100))

    layout.addWidget(lbl)
    layout.addWidget(down_btn)
    layout.addWidget(val_lbl)
    layout.addWidget(up_btn)
    layout.addStretch()

    return row, lambda: val[0]


def _group(title):
    g = QGroupBox(title)
    l = QVBoxLayout(g)
    l.setSpacing(10)
    return g, l


def _tab():
    w = QWidget()
    l = QVBoxLayout(w)
    l.setSpacing(14)
    return w, l


class SettingsWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("CursorVision — Settings")
        self.setMinimumSize(860, 540)
        self.setStyleSheet(SETTINGS_STYLE)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        title = QLabel("Settings")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #2d7dff; background-color: transparent;")
        layout.addWidget(title)

        # Build each settings tab and add to the tab widget
        tabs = QTabWidget()
        tabs.addTab(self._cursor_tab(),      "Cursor Control")
        tabs.addTab(self._click_tab(),       "Click && Gesture")
        tabs.addTab(self._safety_tab(),      "Safety")
        tabs.addTab(self._calibration_tab(), "Calibration")
        tabs.addTab(self._profile_tab(),     "Profile")
        layout.addWidget(tabs)

        self._load_from_disk()

        # Bottom action bar with reset, cancel, and save
        bottom = QWidget()
        bottom.setStyleSheet("background-color: transparent;")
        b_layout = QHBoxLayout(bottom)
        b_layout.setContentsMargins(0, 0, 0, 0)

        reset_btn  = QPushButton("Reset to Defaults")
        cancel_btn = QPushButton("Cancel")
        save_btn   = QPushButton("Save Settings")
        reset_btn.setStyleSheet("background-color: #3a4250; color: white; border-radius: 20px; padding: 10px; font-size: 14px;")
        cancel_btn.setStyleSheet("background-color: #3a4250; color: white; border-radius: 20px; padding: 10px; font-size: 14px;")
        save_btn.setStyleSheet(
            "QPushButton { background-color: #2d7dff; color: white; border-radius: 20px;"
            "padding: 10px; font-size: 14px; min-height: 36px; border: 2px solid #7ab3ff; }"
            "QPushButton:hover { background-color: #4090ff; }"
        )
        reset_btn.clicked.connect(self._on_reset)
        cancel_btn.clicked.connect(self.reject)
        save_btn.clicked.connect(self._on_save)

        b_layout.addWidget(reset_btn)
        b_layout.addStretch()
        b_layout.addWidget(cancel_btn)
        b_layout.addWidget(save_btn)
        layout.addWidget(bottom)

    # Cursor movement controls - sensitivity, smoothing, and dead zone
    def _cursor_tab(self):
        tab, layout = _tab()
        group, g = _group("Cursor Movement")
        row, self.sensitivity = _slider_row("Sensitivity", 1, 100, 50)
        g.addWidget(row)
        row, self.smoothing = _slider_row("Smoothing Strength", 1, 100, 40)
        g.addWidget(row)
        row, self.deadzone = _slider_row("Dead Zone Radius", 0, 50, 10)
        g.addWidget(row)
        layout.addWidget(group)
        return tab

    # Click and gesture controls - blink sensitivity, confidence, cooldown, and wink toggles
    def _click_tab(self):
        tab, layout = _tab()
        group, g = _group("Blink && Wink Detection")
        row, self.blink_sensitivity = _slider_row("Blink Sensitivity", 1, 100, 60)
        g.addWidget(row)
        row, self.confidence = _slider_row("Confidence Threshold", 1, 100, 70)
        g.addWidget(row)

        row, self.get_cooldown = _spinbox_row("Click Cooldown", 100, 2000, 400, " ms")
        g.addWidget(row)
        layout.addWidget(group)

        # Toggles to enable or disable each wink action independently
        wink_group, w = _group("Wink Actions")
        self.left_wink  = QCheckBox("Left Eye Wink  →  Left Click")
        self.right_wink = QCheckBox("Right Eye Wink  →  Right Click")
        self.left_wink.setChecked(True)
        self.right_wink.setChecked(True)
        w.addWidget(self.left_wink)
        w.addWidget(self.right_wink)
        layout.addWidget(wink_group)
        return tab

    # Safety controls - Control cursor behavior when tracking confidence drops
    def _safety_tab(self):
        tab, layout = _tab()
        group, g = _group("Safe Mode && Tracking")
        self.safe_mode   = QCheckBox("Enable Safe Mode when confidence drops below threshold")
        self.auto_pause  = QCheckBox("Auto-pause cursor when face is not detected")
        self.auto_resume = QCheckBox("Auto-resume tracking when face is re-detected")
        for cb in (self.safe_mode, self.auto_pause, self.auto_resume):
            cb.setChecked(True)
            g.addWidget(cb)
        layout.addWidget(group)
        return tab

    # Calibration settings - accuracy display and recalibration trigger
    def _calibration_tab(self):
        tab, layout = _tab()
        group, g = _group("Calibration Settings")

        # Label that displays the last calibration accuracy result.
        acc_row = QWidget()
        acc_row.setStyleSheet("background-color: transparent;")
        a = QHBoxLayout(acc_row)
        a.setContentsMargins(0, 0, 0, 0)
        a.addWidget(QLabel("Last Calibration Accuracy:"))
        self.accuracy_label = QLabel("N/A")
        self.accuracy_label.setStyleSheet("color: #2d7dff; font-weight: bold; background-color: transparent;")
        a.addWidget(self.accuracy_label)
        a.addStretch()
        g.addWidget(acc_row)

        self.auto_suggest = QCheckBox("Suggest recalibration when accuracy drops below threshold")
        self.auto_suggest.setChecked(True)
        g.addWidget(self.auto_suggest)
        recal_btn = QPushButton("Start Recalibration")
        recal_btn.clicked.connect(self._launch_calibration)
        g.addWidget(recal_btn)
        layout.addWidget(group)
        return tab

    # Profile management - create, load, rename, and delete user profiles
    def _profile_tab(self):
        tab, layout = _tab()
        group, g = _group("User Profiles")

        # Shows which profile is currently active
        active_row = QWidget()
        active_row.setStyleSheet("background-color: transparent;")
        ar = QHBoxLayout(active_row)
        ar.setContentsMargins(0, 0, 0, 0)
        ar.addWidget(QLabel("Active Profile:"))
        self.active_profile_label = QLabel("None")
        self.active_profile_label.setStyleSheet("color: #2d7dff; font-weight: bold; background-color: transparent;")
        ar.addWidget(self.active_profile_label)
        ar.addStretch()
        g.addWidget(active_row)

        g.addWidget(QLabel("Saved Profiles:"))
        self.profile_list = QListWidget()
        self.profile_list.setMinimumHeight(120)
        # Load existing profiles from the profiles folder
        self._populate_profile_list()
        g.addWidget(self.profile_list)

        name_row = QWidget()
        n = QHBoxLayout(name_row)
        n.setContentsMargins(0, 0, 0, 0)
        lbl = QLabel("Profile Name:")
        lbl.setMinimumWidth(110)
        self.profile_name = QLineEdit()
        self.profile_name.setPlaceholderText("Enter name...")
        n.addWidget(lbl)
        n.addWidget(self.profile_name)
        g.addWidget(name_row)

        btn_row = QWidget()
        b = QHBoxLayout(btn_row)
        b.setContentsMargins(0, 0, 0, 0)
        b.setSpacing(8)
        create_btn = QPushButton("Create")
        load_btn   = QPushButton("Load")
        rename_btn = QPushButton("Rename")
        delete_btn = QPushButton("Delete")
        load_btn.setStyleSheet("background-color: #3a4250; color: white; border-radius: 20px; padding: 10px; font-size: 14px;")
        rename_btn.setStyleSheet("background-color: #3a4250; color: white; border-radius: 20px; padding: 10px; font-size: 14px;")
        delete_btn.setStyleSheet("background-color: #c0392b; color: white; border-radius: 20px; padding: 10px; font-size: 14px;")
        create_btn.clicked.connect(self._on_create)
        load_btn.clicked.connect(self._on_load)
        rename_btn.clicked.connect(self._on_rename)
        delete_btn.clicked.connect(self._on_delete)
        for btn in (create_btn, load_btn, rename_btn, delete_btn):
            b.addWidget(btn)
        g.addWidget(btn_row)
        layout.addWidget(group)
        return tab

    # Reads the profiles folder and populates the list widget
    def _populate_profile_list(self):
        self.profile_list.clear()
        if PROFILES_DIR.exists():
            for p in sorted(PROFILES_DIR.glob("*.json")):
                self.profile_list.addItem(p.stem)

    # Closes settings and opens Demo Mode
    def _launch_calibration(self):
        main_window = self.parent()
        if main_window and hasattr(main_window, 'menu_buttons_panel'):
            self.accept()
            main_window.menu_buttons_panel.demo_button.click()
        else:
            QMessageBox.information(self, "Recalibration", "Please use Calibration Mode from the main menu.")

    def _on_create(self):
        name = self.profile_name.text().strip()
        if not name:
            QMessageBox.warning(self, "Profile", "Please enter a profile name.")
            return
        PROFILES_DIR.mkdir(exist_ok=True)
        profile_path = PROFILES_DIR / f"{name}.json"
        if profile_path.exists():
            QMessageBox.warning(self, "Profile", "A profile with that name already exists.")
            return
        # Save a new profile with the current UI settings
        with open(profile_path, "w") as f:
            json.dump(self._collect_settings(), f, indent=2)
        self._populate_profile_list()
        self.profile_name.clear()

    # Loads the selected profile from disk and applies its settings to the UI
    def _on_load(self):
        item = self.profile_list.currentItem()
        if not item:
            QMessageBox.warning(self, "Profile", "Please select a profile to load.")
            return
        name = item.text()
        profile_path = PROFILES_DIR / f"{name}.json"
        if not profile_path.exists():
            QMessageBox.warning(self, "Profile", "Profile file not found.")
            return
        try:
            with open(profile_path, "r") as f:
                config = json.load(f)
            self._apply_settings(config)
            self.active_profile_label.setText(name)
            ACTIVE_FILE.write_text(name)
        except Exception as e:
            QMessageBox.warning(self, "Profile", f"Failed to load profile: {e}")

    def _on_rename(self):
        item = self.profile_list.currentItem()
        new_name = self.profile_name.text().strip()
        if not item or not new_name:
            QMessageBox.warning(self, "Profile", "Select a profile and enter a new name.")
            return
        old_path = PROFILES_DIR / f"{item.text()}.json"
        new_path = PROFILES_DIR / f"{new_name}.json"
        if new_path.exists():
            QMessageBox.warning(self, "Profile", "A profile with that name already exists.")
            return
        old_path.rename(new_path)
        # Update active profile file if the renamed profile was active
        if ACTIVE_FILE.exists() and ACTIVE_FILE.read_text() == item.text():
            ACTIVE_FILE.write_text(new_name)
            self.active_profile_label.setText(new_name)
        self._populate_profile_list()
        self.profile_name.clear()

    def _on_delete(self):
        item = self.profile_list.currentItem()
        if not item:
            QMessageBox.warning(self, "Profile", "Please select a profile to delete.")
            return
        if QMessageBox.question(self, "Delete", f"Delete '{item.text()}'?",
                                QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            profile_path = PROFILES_DIR / f"{item.text()}.json"
            if profile_path.exists():
                profile_path.unlink()
            # Clear active profile tracking if deleted profile was active
            if ACTIVE_FILE.exists() and ACTIVE_FILE.read_text() == item.text():
                ACTIVE_FILE.unlink()
                self.active_profile_label.setText("None")
            self._populate_profile_list()

    # Collects all current UI values into a config dict
    def _collect_settings(self):
        return {
            "sensitivity":           self.sensitivity.value(),
            "smoothing":             self.smoothing.value(),
            "deadzone":              self.deadzone.value(),
            "blink_sensitivity":     self.blink_sensitivity.value(),
            "confidence_threshold":  self.confidence.value(),
            "click_cooldown_ms":     self.get_cooldown(),
            "left_wink_enabled":     self.left_wink.isChecked(),
            "right_wink_enabled":    self.right_wink.isChecked(),
            "safe_mode_enabled":     self.safe_mode.isChecked(),
            "auto_pause_on_no_face": self.auto_pause.isChecked(),
            "auto_resume":           self.auto_resume.isChecked(),
            "auto_suggest_recal":    self.auto_suggest.isChecked(),
        }

    # Applies a config dict to all UI controls
    def _apply_settings(self, config):
        self.sensitivity.setValue(config.get("sensitivity", 50))
        self.smoothing.setValue(config.get("smoothing", 40))
        self.deadzone.setValue(config.get("deadzone", 10))
        self.blink_sensitivity.setValue(config.get("blink_sensitivity", 60))
        self.confidence.setValue(config.get("confidence_threshold", 70))
        self.left_wink.setChecked(config.get("left_wink_enabled", True))
        self.right_wink.setChecked(config.get("right_wink_enabled", True))
        self.safe_mode.setChecked(config.get("safe_mode_enabled", True))
        self.auto_pause.setChecked(config.get("auto_pause_on_no_face", True))
        self.auto_resume.setChecked(config.get("auto_resume", True))
        self.auto_suggest.setChecked(config.get("auto_suggest_recal", True))

    # Collects all settings and saves them to the active profile
    def _on_save(self):
        active = self.active_profile_label.text()
        if active == "None":
            QMessageBox.warning(self, "Settings", "Please load or create a profile before saving.")
            return
        profile_path = PROFILES_DIR / f"{active}.json"
        try:
            PROFILES_DIR.mkdir(exist_ok=True)
            with open(profile_path, "w") as f:
                json.dump(self._collect_settings(), f, indent=2)
            QMessageBox.information(self, "Settings", f"Settings saved to profile '{active}'.")
        except Exception as e:
            QMessageBox.warning(self, "Settings", f"Failed to save settings: {e}")
        self.accept()

    # Loads the last active profile from disk on open
    def _load_from_disk(self):
        if not ACTIVE_FILE.exists():
            return
        name = ACTIVE_FILE.read_text().strip()
        profile_path = PROFILES_DIR / f"{name}.json"
        if not profile_path.exists():
            return
        try:
            with open(profile_path, "r") as f:
                config = json.load(f)
            self._apply_settings(config)
            self.active_profile_label.setText(name)
        except Exception:
            pass

    # Restores all sliders and checkboxes to their default values
    def _on_reset(self):
        if QMessageBox.question(self, "Reset", "Reset all settings to defaults?",
                                QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            self.sensitivity.setValue(50)
            self.smoothing.setValue(50)
            self.deadzone.setValue(10)
            self.blink_sensitivity.setValue(50)
            self.confidence.setValue(50)
            self.left_wink.setChecked(True)
            self.right_wink.setChecked(True)
            self.safe_mode.setChecked(True)
            self.auto_pause.setChecked(True)
            self.auto_resume.setChecked(True)
            self.auto_suggest.setChecked(True) 