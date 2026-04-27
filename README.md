# CursorVision

CursorVision is an accessibility-focused software project that allows users to control cursor movement and basic mouse actions using webcam based face and eye tracking.

The motivation for this project comes from seeing how difficult computer interaction can become for people who temporarily or permanently lose the ability to use their arms. CursorVision offers a lower-cost assistive technology approach by using a standard webcam instead of specialized hardware.

The system is built with Python using OpenCV, MediaPipe, PyQt5, and TensorFlow. The main runtime uses real-time webcam input, facial landmark detection, gaze estimation, cursor smoothing, and wink-based click detection.

---

## Core Features

- Real-time webcam video capture
- Face and eye landmark tracking using MediaPipe
- Continuous gaze/look estimation from frame captures
- Cursor movement using OS-level cursor control
- Cursor smoothing to reduce jitter
- Wink-based clicking:
  - Left wink = left click
  - Right wink = right click
  - Both eyes blink = ignored
- Triple-wink disable gaze based control
- Interactive calibration mode
- TensorFlow model trained from calibration samples
- Local processing for added privacy

---

## Technology List

- Python
- OpenCV
- MediaPipe
- TensorFlow
- NumPy
- PyQt5
- Windows cursor control using OS APIs

---

## Project Structure

---
Run using main.py
---

```text
cursor_vision/
    main.py
    calibration.py
    cursor_vision_session.py
    cursor_controller.py
    look_direction.py
    face_features.py
    tensorflow_model.py
    mesh_map.py
    web_cam.py
    values_tracking.py
    ui/
        main_menu.py
        camera_view.py
        settings_menu.py

models/
    face_landmarker.task
    gaze_smoother.keras