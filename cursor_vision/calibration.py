#Kody Graham
#WIll contain the logic for the calibration UI and datapoints

import math
import cv2
from pathlib import Path
import json
import time
import mediapipe as mp
import mesh_map
from look_direction import LookDirection
from face_features import build_feature_dict

class Calibration:

    def __init__(self, numberOfCalPoints = 9):

        self.look_direction = LookDirection()

        self.numberOfCalPoints= numberOfCalPoints
        self.calibration_positions = []
        self.saved_calibration_data = []

        self.window_name = "CursorVision - Calibration Mode"
        self.model_path = Path(__file__).resolve().parent.parent / "models" / "face_landmarker.task"

        self.frame_width = None
        self.frame_height = None
        self.cur_point_index = 0
        self.point_radius = 18

        self.samples_per_point = 25
        self.capture_active = False
        self.capture_buffer = []

        self.state = "menu"



    #Start calibration
    def startCalibration(self):
        self.state = "neutral"
        self.cur_point_index = 0
        self.saved_calibration_data = []
        self.capture_active = False
        self.capture_buffer = []
        self.look_direction.clear_neutral_eye_center()

        if not self.calibration_positions:
            self.createCalibrationPoints()

    #Draw calibration screen
    def drawCalibrationMenu(self, frame):

        frame[:] = (0,0,0)
        title = "CursorVision - Calibration Mode"
        line1 = "Press 'ENTER' to start calibration"
        line2 = "Press 'ESC' to quit at any time"
        line3 = "During Calibration: 'ENTER' will capture a burst"
        line4 = f"of {self.samples_per_point} calibration values for each point"

        cv2.putText(frame,title, (self.frame_width//2 -260,60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 3)

        cv2.line(frame, (self.frame_width//2 -265,70), (self.frame_width//2 +260,70), (255, 0, 0), 2)

        cv2.putText(frame, line1, (self.frame_width//2 -215, 120), cv2.FONT_HERSHEY_SIMPLEX, .8, (255,255,255), 1)

        cv2.putText(frame, line2, (self.frame_width//2 -203,180), cv2.FONT_HERSHEY_SIMPLEX, .8, (255,255,255), 1)

        cv2.putText(frame, line3, (self.frame_width//2 -300,240), cv2.FONT_HERSHEY_SIMPLEX, .8, (0,0,255), 1)

        cv2.putText(frame, line4, (self.frame_width//2 -250,280), cv2.FONT_HERSHEY_SIMPLEX, .8, (0,0,255), 1)


        return frame

    def drawNeutralScreen(self, frame):
        frame[:] = (0,0,0)
        center = (self.frame_width//2,self.frame_height//2)

        cv2.putText(frame, "Step 1: Set Neutral", (self.frame_width // 2 - 160, 70), cv2.FONT_HERSHEY_SIMPLEX, 1,(0, 0, 255), 3)
        cv2.putText(frame, "Look at the center dot and press ENTER", (self.frame_width // 2 - 250, 120),cv2.FONT_HERSHEY_SIMPLEX, .8, (255, 255, 255), 2)
        cv2.putText(frame, "R = reset    ESC = quit", (self.frame_width // 2 - 135, 165), cv2.FONT_HERSHEY_SIMPLEX, .7,(255, 255, 255), 1)

        cv2.circle(frame, center, self.point_radius +4, (255,255, 255), 2)
        cv2.circle(frame, center, self.point_radius, (0,0,255), 2)
        return frame

    #Create points
    def createCalibrationPoints(self):
        if self.frame_width is None or self.frame_height is None:
            return

        self.calibration_positions.clear()

        normalized_point_positions = [
            #First row
            (.15,.15), (.50,.15),(.85,.15),
            #Second row
            (.15,.50),(.50,.50),(.85,.50),
            #Third row
            (.15,.85), (.50,.85), (.85,.85)]

        for x,y in normalized_point_positions[:self.numberOfCalPoints]:
            x = int(x * self.frame_width)
            y = int(y * self.frame_height)
            self.calibration_positions.append((x,y))

    #Creates and returns the mediapipe face landmarker same logic as my web_cam class but creating it here so I can
    #include the target and UI in the loop
    #Copied from demo mode
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

    def buildCalibrationData(self, face_landmarks, frame_shape):
        return build_feature_dict(self.look_direction,face_landmarks,frame_shape)

    #Draw points
    def drawCalibrationPoints(self, frame):

        for i, (x, y) in enumerate(self.calibration_positions):
            if i < self.cur_point_index:
                color = (0, 255, 0)
                radius = self.point_radius

            elif i == self.cur_point_index and self.state == "running":
                color = (0, 0, 255)
                radius = self.point_radius + 4

            else:
                color = (180, 180, 180)
                radius = self.point_radius

            cv2.circle(frame, (x,y), radius, color, 2)
            cv2.circle(frame, (x,y), radius + 4, (255,255,255), 2)

            if i == self.cur_point_index and self.capture_active:
                burst_counter = f"{len(self.capture_buffer)}/{self.samples_per_point}"
                counter_size, _ = cv2.getTextSize(burst_counter, cv2.FONT_HERSHEY_SIMPLEX, .4, 1)

                text_x = x - (counter_size[0] // 2)-3
                text_y = y - radius - 18

                cv2.putText(frame,burst_counter, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, .5, (0,255,0), 2)

    def drawCalHUD(self, frame):
        cur_point = f"Point {min(self.cur_point_index +1, len(self.calibration_positions))}/ {len(self.calibration_positions)}"
        label = "Look at the RED point, "
        label1 = "and then press ENTER to capture a burst"
        label2 = "R = reset    ESC = quit"

        cv2.putText(frame, label, (180, 145), cv2.FONT_HERSHEY_SIMPLEX, .8, (0,0,255), 2)
        cv2.putText(frame, label1, (60, 180), cv2.FONT_HERSHEY_SIMPLEX, .8, (0,0,255), 2)

        cv2.putText(frame,cur_point, (25, self.frame_height - 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

        cv2.putText(frame, label2, (130,350), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,0), 2)


    #Save calibration data
    def startBurstCapture(self):
        if self.state != "running":
            return

        if self.cur_point_index >= len(self.calibration_positions):
            return
        self.capture_active = True
        self.capture_buffer = []

    def appendBurstData(self,feature_dict):
        if not self.capture_active or feature_dict is None:
            return

        if self.cur_point_index >= len(self.calibration_positions):
            self.capture_active = False
            return

        target_x, target_y = self.calibration_positions[self.cur_point_index]

        data = {
            "point_index" : int(self.cur_point_index),
            "screen_x": int(target_x),
            "screen_y": int(target_y),
            "frame_width": int(self.frame_width),
            "frame_height": int(self.frame_height),
            "screem_x_norm": float(target_x)/ max(float(self.frame_width - 1), 1),
            "screem_y_norm": float(target_y)/ max(float(self.frame_height - 1), 1),
            "features": feature_dict
        }
        self.capture_buffer.append(data)

        if len(self.capture_buffer) >= self.samples_per_point:
            self.saved_calibration_data.extend(self.capture_buffer)
            self.capture_buffer = []
            self.capture_active = False
            self.cur_point_index += 1

            if self.cur_point_index >= len(self.calibration_positions):
                self.state = "done"


    def saveCalibrationPoints(self, frame, file_name = "calibration_data.json"):
        file_path = Path(__file__).resolve().parent / file_name

        payload= {
            "format_version": 2,
            "values_per_point": self.samples_per_point,
            "screen_width": self.frame_width,
            "screen_height": self.frame_height,
            "neutral_horizontal": self.look_direction.neutral_horizontal_pos,
            "neutral_vertical": self.look_direction.neutral_vertical_pos,
            "data_values": self.saved_calibration_data,
        }

        with open(file_path, "w", encoding= "utf-8") as file:
            json.dump(payload, file, indent=4)

        print(f"Calibration data saved to {file_path}")
        label_temp = "Saved Sample Values Successfully"
        cv2.putText(frame, label_temp, (50, 400), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        cv2.imshow(self.window_name, frame)
        cv2.waitKey(1500)

    #Reset calibration data
    def resetCalibrationPoints(self):
        self.cur_point_index = 0
        self.saved_calibration_data = []
        self.state = "menu"
        self.capture_active = False
        self.capture_buffer = []
        self.look_direction.clear_neutral_eye_center()

    def drawMainScreen(self,frame):

        frame[:] = (0,0,0)

        menu_label1 = "Calibration Complete!"
        menu_label2 = "Press S to save"
        menu_label3 = "Press R to recalibrate"
        menu_label4 = "Press ESC to quit"
        menu_label5 = f"Data Point Sets Captured: {len(self.saved_calibration_data)}"

        cv2.putText(frame, menu_label1, (40,90), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 3)

        cv2.putText(frame, menu_label2, (40,160), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)

        cv2.putText(frame, menu_label3, (40,205), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)

        cv2.putText(frame, menu_label4, (40,250), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)

        cv2.putText(frame, menu_label5, (40,295), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)
        return frame


    def runCalibration(self, frame, key, face_landmarks=None, data_save=None):
        if self.frame_width is None or self.frame_height is None:
            self.frame_height, self.frame_width = frame.shape[:2]
            self.createCalibrationPoints()

        if self.state == "menu":
            frame = self.drawCalibrationMenu(frame)

            if key == 13:
                self.startCalibration()

        elif self.state == "neutral":
            frame = self.drawNeutralScreen(frame)

            if key == 13:
                if face_landmarks is not None:
                    self.look_direction.neutral_eye_center(face_landmarks, frame.shape)
                    self.state = "running"


            elif key == ord('r'):
                self.resetCalibrationPoints()
                self.createCalibrationPoints()

        elif self.state == "running":
            self.drawCalibrationPoints(frame)
            self.drawCalHUD(frame)

            if key ==13 and not self.capture_active:
                self.startBurstCapture()

            elif key == ord('r'):
                self.resetCalibrationPoints()
                self.createCalibrationPoints()

            if self.capture_active:
                self.appendBurstData(data_save)
        elif self.state == "done":
            self.drawCalibrationPoints(frame)
            frame = self.drawMainScreen(frame)

            if key == ord('s'):
                self.saveCalibrationPoints(frame)

            elif key == ord('r'):
                self.resetCalibrationPoints()
                self.createCalibrationPoints()

        return frame

    def run(self):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            raise IOError("Cannot open webcam")

        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        self.start_time = time.time()

        with self.create_landmarker() as landmark:
            while True:
                working, camera_frame = cap.read()
                if not working:
                    break

                camera_frame = cv2.flip(camera_frame, 1)
                frame_bgr =camera_frame.copy()

                frame_rgb = cv2.cvtColor(camera_frame, cv2.COLOR_BGR2RGB)
                mp_image = mp.Image(image_format= mp.ImageFormat.SRGB, data=frame_rgb)
                timestamp_ms = int((time.time() - self.start_time) * 1000)

                result = landmark.detect_for_video(mp_image, timestamp_ms)

                data_save = None
                face_found = False
                face_landmarks = None

                if result.face_landmarks:
                    face_found = True
                    face_landmarks = result.face_landmarks[0]
                    mesh_map.draw_landmarks(frame_bgr, face_landmarks)
                    data_save = self.buildCalibrationData(face_landmarks, frame_bgr.shape)

                status = "FACE: FOUND" if face_found else "FACE: NOT FOUND"
                status_col = (0,255,0) if face_found else (0,0,255)

                if face_found:
                    cv2.putText(frame_bgr,status, (430, 460), cv2.FONT_HERSHEY_SIMPLEX, 1, status_col, 2)
                else:
                    cv2.putText(frame_bgr,status,(353, 460), cv2.FONT_HERSHEY_SIMPLEX, 1, status_col, 2)

                key = cv2.waitKey(1) & 0xFF
                frame_bgr = self.runCalibration(frame_bgr, key, face_landmarks=face_landmarks, data_save = data_save)
                cv2.imshow(self.window_name, frame_bgr)

                if key == 27:
                    break

        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    Calibration().run()



