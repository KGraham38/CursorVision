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
EXECUTION/BUILD NOTES:
---

*JUST PERSONAL NOTES WHILE THINKING HOW TO STRUCTURE EVERYTHING*

Option 1:
- The easiest way to build an application like this in my head would be if you imagine you took a screenshot with your webcam, 
this rectangle image will be what I am referring to when I say working area. So start with a small safe area, about the center 15% of the working area,
from there divide the remaining working area (not including the safe area obviously) into equal sections which extend all the way from each corner
of the safe area to the corner the corresponding corners on the working area. We now have 5 distinct areas: left of safe area, right of safe area, above safe area.
and below safe area. Then we just set the cursor to move anytime the calculated area the user is looking at, from our TensorFlow Agent, is in one of those quadrants.
- With this set up we will negate a lot of errors that I could see stemming from the fact that the webcam is not in the center of the computer screen. Meaning if we
try to achieve pinpoint accuracy expecting that if we look at a dot in the center of the screen it will look to the camera like we are looking directly into it is illogical.
This is the effect I am trying to prevent by adding the safe area (where looking at that part of the image has no effect), and the more quadrant based movement.
- Cons: Will only allow for one direction of travel by the cursor at a time, meaning either +-x or +-y but never both at the same time.
- Potential Solution: More quadrants, instead of 4 areas for movement parallel to xy axis's, still keep those but split each quadrant 3 more times for a total of 16,
as well as swap to +-dx & +-dy to make movement look even more natural. 
This way the quadrants are still big enough to allow for camera/screen view not being identical but allow for more natural movement.

Option 2 for control:
- Rely more on my TensorFlow regression model using the face/eye landmarks to estimate offset for gx/gy based on neutral view. Then add a curve so small offsets = slower speed and big offset = faster.
- Maybe use a 9 point calibration coordinate system since this will be a more directional/speed based movement system.

---