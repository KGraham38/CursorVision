Will start building an accessibility feature to control mouse movement and actions based on eye movement.
I have personally had three different family members who have either temporarily or permanently lost the ability to use their arms due to extreme injuries.
Using Python and TensorFlow I will design and implement a solution to this problem that no doubt millions of people worldwide face, for a variety of reasons, in their daily lives.
Again, this will be an as I have time project so long gaps between commits are to be expected. 

---
PROJECT EXPECTED FEATURES:
---



---
PROJECT STRUCTURE:
---
cursor_vision/

    main.py
    camera/
        webcam_stream.py
    vision/
        landmarks.py
        features.py
        blink.py
    calibration/
        calibration_ui.py
        data_collector.py
    model/
        train_regressor.py
        gaze_regressor.py
        serialization.py
    control/
        smoothing.py
        cursor_controller.py
    utils/
        config.py
        metrics.py
        logging.py
    assets/
    README.md
- Just expected; definitely subject to change.
---