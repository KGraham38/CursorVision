#Kody Graham
#Will have the logic for our demonstration for use at the UCA symposium

from look_direction import LookDirection

import mesh_map
import cv2
import numpy as np
import time
import random
import mediapipe as mp
from pathlib import Path


class DemoMode:

    def __init__(self):
        self.window_name = "CursorVision - Demo Mode"
        self.model_path = Path(__file__).resolve().parent.parent / "models" / "face_landmarker.task"

        self.look_direction = LookDirection()

        #Had to add these multipliers to make slight eye movements move the cursor further
        self.look_direction.horizontal_multiplier = 2200.0
        self.look_direction.vertical_multiplier = 5200.0

        self.look_direction.cursor_dot_speed = 4.0
        self.look_direction.show_lines = True

        self.frame_width = None
        self.frame_height = None
        self.last_face_landmarks = None
        self.start_time = 0
        self.targets = []
        self.blown_up_targets = []
        self.score = 0

    #Creates and returns the mediapipe face landmarker same logic as my web_cam class but creating it here so I can
    #include the target and UI in the loop
    def create_landmarker(self):
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model file not found: {self.model_path}")

        options = mp.tasks.vision.FaceLandmarkerOptions(
            base_options=mp.tasks.BaseOptions(model_asset_path= str(self.model_path)),
            running_mode=mp.tasks.vision.RunningMode.VIDEO,
            num_faces=1,
            min_face_detection_confidence=0.5,
            min_face_presence_confidence=0.5,
            min_tracking_confidence=0.5,
            output_face_blendshapes=False,
            output_facial_transformation_matrixes=False, )

        return mp.tasks.vision.FaceLandmarker.create_from_options(options)

    #Just sets the frame size and spawns the targets
    def setup(self, frame):
        if self.frame_width is not None:
            return
        self.frame_height, self.frame_width = frame.shape[:2]
        self.spawn_targets()

    #Handles the logic for displaying my targets
    def spawn_targets(self):

        self.targets.clear()
        self.blown_up_targets.clear()
        self.score = 0

        radius = 24
        colors = [(255, 0, 0), (0,0,255)]

        top_row_y = 115
        bottom_row_y = self.frame_height -70
        left_column_x = 70
        right_column_x = self.frame_width - 70

        target_positions = []

        for i in range(4):
            #space targets evenly top and bottom
            x = int((i+1) * self.frame_width / 5)
            target_positions.append((x, top_row_y))
            target_positions.append((x, bottom_row_y))

        for i in range(3):
            #space y left side
            y = int((i+1)* self.frame_height / 4)
            target_positions.append((left_column_x, y))
            target_positions.append((right_column_x, y))

        #Build the target dict and add to the targets list
        for x, y in target_positions:
            x = max(radius + 5,min(self.frame_width-radius - 5,x))
            y = max(radius +5,min(self.frame_height-radius - 5,y))
            self.targets.append({"x": x, "y": y, "radius": radius, "color": random.choice(colors), "broke": False})

    #Reset the demo
    def reset(self):
        if self.frame_width is not None:
            self.spawn_targets()

    #Reset both my current look position dot and my simulated cursor dot
    def reset_dots(self):
        self.look_direction.current_look_dot_x = None
        self.look_direction.current_look_dot_y = None
        self.look_direction.cursor_look_dot_x = None
        self.look_direction.cursor_look_dot_y = None

    #Handles my explosion effect
    def explode_targets(self, target):
        target["broke"] = True

        #Create 15 fragment pieces for each explosion
        for i in range(15):
            self.blown_up_targets.append({"x": float(target["x"] + random.randint(-target["radius"] // 2, target["radius"] // 2)),
                                            "y": float(target["y"] + random.randint(-target["radius"] // 2, target["radius"] // 2)),
                                            "vx": random.uniform(-4.0,4.0) , "vy": random.uniform(-7.5,-2.5), "gravity": .42, "size": random.randint(3,6),
                                            "color": target["color"], "move": True })

    #Method to update target piece motion and track my target hits
    def update_targets(self, hit_position):

        #Hit position is indicated by the red dot when running demo mode, it is the current est look location
        if hit_position is not None:
            hx, hy = hit_position

            #Just check for all targets not already broken
            for target in self.targets:
                if target["broke"]:
                    continue

                dx = hx - target["x"]
                dy = hy - target["y"]

                #This took some fine tuning, ended up just using the squared distance and the times 2 is just a little
                #helper to account for inaccuracy and look dot radius
                if dx*dx + dy *dy <= target["radius"]* target["radius"] * 2:
                    self.explode_targets(target)
                    self.score +=1

        #Move my blown up target pieces
        for piece in self.blown_up_targets:
            piece["x"] += piece["vx"]
            piece["y"] += piece["vy"]
            piece["vy"] += piece["gravity"]
            piece["move"] = piece["y"] - piece["size"] <= self.frame_height

        self.blown_up_targets = [piece for piece in self.blown_up_targets if piece["move"]]

    #Draws all of my targets and target fragments
    def draw_targets(self,frame):

        #Draw targets
        for target in self.targets:
            if not target["broke"]:
                x = target["x"]
                y = target["y"]
                radius = target["radius"]
                color = target["color"]

                cv2.circle(frame, (x,y), radius, color, 4)
                cv2.circle(frame, (x,y), int(radius* .8), (255,255,255), 3)
                cv2.circle(frame, (x,y), int(radius*.4), color, -1)

        #Draw target pieces
        for piece in self.blown_up_targets:
            if piece["move"]:
                x = int(piece["x"])
                y = int(piece["y"])
                size = piece["size"]
                cv2.rectangle(frame, (x-size,y-size), (x+size,y+size), piece["color"], -1)

    #Pretty self-explanatory
    def draw_ui(self,frame, face_found, hit_position):
        remaining_targets = sum(not target["broke"] for target in self.targets)

        if face_found:
            cv2.putText(frame, "FACE: FOUND",(10,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

        else:
            cv2.putText(frame, "FACE: NOT FOUND",(10,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)

        if not self.look_direction.neutral_set:
            cv2.putText(frame, "Press 'C' to Calibrate", (10,69), cv2.FONT_HERSHEY_SIMPLEX, .8, (255,0,0), 2)

        cv2.putText(frame, f"Score: {self.score}", (10,self.frame_height - 20), cv2.FONT_HERSHEY_SIMPLEX, .8, (255,255,255), 2)

        cv2.putText(frame, f"Targets Left: {remaining_targets}", (180, self.frame_height-20), cv2.FONT_HERSHEY_SIMPLEX, .8, (255,255,255), 2)

        if remaining_targets == 0:
            cv2.putText(frame,"All Targets Broken! To Reset Press 'T'", (80,100),cv2.FONT_HERSHEY_SIMPLEX, .8, (0,0,255), 2)

        if hit_position is not None:
            cv2.circle(frame, hit_position, 12, (0,0,255), 2)
            cv2.putText(frame,"Look at the Targets!", (hit_position[0] + 12, hit_position[1]-12), cv2.FONT_HERSHEY_SIMPLEX, .38, (0,0,255), 1)

    #Just my simple listener for user keyboard input
    def keyboard_listener(self, key_pressed, frame_shape):
        #Show/hide lines
        if key_pressed == ord('l'):
            self.look_direction.show_lines = not self.look_direction.show_lines
        #reset dots to center and unset callibration
        elif key_pressed == ord('r'):
            self.reset_dots()
            self.look_direction.neutral_set = False

        #reset targets
        elif key_pressed == ord('t'):
            self.reset()
        #Calibrate
        elif key_pressed == ord('c') and self.last_face_landmarks is not None:
            self.look_direction.neutral_eye_center(self.last_face_landmarks, frame_shape)
            self.reset_dots()

    #My main loop for the demo
    def run(self):
        capture = cv2.VideoCapture(0)
        if not capture.isOpened():
            raise IOError("Cannot open webcam")

        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        self.start_time = time.time()

        #Create my mediapipe landmarker
        with self.create_landmarker() as landmark:
            while True:
                working, camera_frame = capture.read()
                if not working:
                    break

                camera_frame = cv2.flip(camera_frame, 1)
                self.setup(camera_frame)

                frame_height, frame_width = camera_frame.shape[:2]

                #Black background
                frame_bgr = np.zeros((frame_height, frame_width, 3), np.uint8)

                #To be able to use rgb
                frame_rgb = cv2.cvtColor(camera_frame, cv2.COLOR_BGR2RGB)

                #Wrap my frame into a mediapipe image obj
                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)

                timestamp_ms = int((time.time() - self.start_time) * 1000)

                #detect the landmarks
                result = landmark.detect_for_video(mp_image, timestamp_ms)

                face_found = False
                hit_position = None

                if result.face_landmarks:
                    face_found = True
                    self.last_face_landmarks = result.face_landmarks[0]

                    #Draw landmarks and cursors
                    mesh_map.draw_landmarks(frame_bgr, self.last_face_landmarks)
                    self.look_direction.draw(frame_bgr, self.last_face_landmarks)
                    hit_position = self.look_direction.current_look_point()

                self.update_targets(hit_position)
                self.draw_targets(frame_bgr)
                self.draw_ui(frame_bgr, face_found, hit_position)

                #Show frame
                cv2.imshow(self.window_name, frame_bgr)

                #Listner to quit at any time
                key_pressed = cv2.waitKey(1) & 0xFF
                if key_pressed == 27:
                    break
                self.keyboard_listener(key_pressed, camera_frame.shape)

        #close webcam and cv window
        capture.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    DemoMode().run()