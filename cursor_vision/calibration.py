#Kody Graham
#WIll contain the logic for the calibration UI and datapoints

import math
import cv2

class Calibration:

    def __init__(self, numberOfCalPoints = 9):
        self.numberOfCalPoints= numberOfCalPoints
        self.calibration_positions = []
        self.saved_calibration_data = []

        self.window_name = "CursorVision - Calibration Mode"
        self.model_path = Path(__file__).resolve().parent.parent / "models" / "face_landmarker.task"

        self.frame_width = None
        self.frame_height = None
        self.cur_point_index = 0
        self.point_radius = 18

        sel.state = "menu"



    #Start calibration
    def startCalibration(self):
        self.state = "running"
        self.cur_point_index = 0
        self.saved_calibration_data = []

        if not self.calibration_positions:
            self.createCalibrationPoints()

    #Draw calibration screen
    def drawCalibrationMenu(self):
        title = "CursorVision - Calibration Mode"
        line1 = "Press 'ENTER' to start calibration"
        line2 = "Press 'ESC' to quit at any time"
        line3 = "During calibration: 'SPACE' to save point, 'R' to reset"

        cv2.putText(frame,title, (40,70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 3)

        cv2.putText(frame, line1, (40, 140), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)

        cv2.putText(frame, line2, (40,185), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)

        cv2.putText(frame, line3, (40,230), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)

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

    #Draw points
    def drawCalibrationPoints(self, calibration_positions):

        for x, y in calibration_positions:
            x = max(radius + 5,min(self.frame_width-radius - 5,x))
            y = max(radius +5,min(self.frame_height-radius - 5,y))
            self.targets.append({"x": x, "y": y, "radius": radius, "color": random.choice(colors), "broke": False})

    #Save calibration data
    def saveCalibrationPoints(self):
        pass

    #Reset calibration data
    def resetCalibrationPoints(self):
        pass


    def runCalibration(self):
        self.drawCalibrationMenu()


