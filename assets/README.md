Will start building an accessibility feature to control cursor movement and actions based on eye movement.
I have personally had three different family members who have either temporarily or permanently lost the ability to use their arms due to extreme injuries.
Using Python and TensorFlow I will design and implement a solution to this problem that no doubt millions of people worldwide, for a variety of reasons, face in their daily lives.
Again, this will be an as I have time project so long gaps between commits are to be expected. 

---
PROJECT EXPECTED FEATURES:
---
--- Core System ---
- Real time webcam video capture
- Face detection and eyr landmark extraction
- Continuous look estimation from the live video
- Stable performance on built in webcam which can be low quality (might be an issue to address but I will get it stable on my system first)

--- AI/ML Features ---
- Supervised learning with per user calibration data
- TensorFlow based regression mapping model:
  - user eye/face features to screen coordinates
- Small neural net
- Model training locally after calibration
- Save models per user profile

--- Calibration Features ---
- Interactive on screen calibration
- Multi point grid
- Collection of samples per calibration point
- Post calibration accuracy check
- Suggestion for recalibration if error % reaches a threshold

--- Cursor Control & Interaction ---
- Smooth the cursor movement using movement filter
- Probably just built in settings menu to balance responsiveness/speed
- Stop movement if confidence is low

--- Click Detection ---
- Left eye wink = left mouse click
- Right eye wink = right mouse click
- Normal blink (both eyes) = Ignore (Might have to implement a confidence interval for each individual eye blink to make this feature reliable)
- Maybe a cooldown for between more than triple clicks as I cant think of any benefit to spam clicking more than that

--- Debugging ---
- Real time fps and latency monitoring
- Maybe a debug overlay to show landmarks and calculated look point

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