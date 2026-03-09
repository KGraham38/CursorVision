from look_direction import LookDirection
from web_cam import Webcam

class DemoMode:

    def __init__(self):
        self.webcam = Webcam()
        self.look_direction = LookDirection()

    def run(self):
        self.webcam.run(self.look_direction)

if __name__ == "__main__":
    DemoMode().run()