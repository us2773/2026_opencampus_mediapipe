from collections import deque
from .check_visibility import check_visibility

class SwingDetector:
    def __init__(self):
        self.frames = deque(maxlen=15)

    def detect(self, landmarks):
        if not check_visibility([landmarks[15], landmarks[16]]) :
            return False
        else :
            left_wrist = landmarks[15].y
            right_wrist = landmarks[16].y
            self.frames.append((left_wrist + right_wrist) / 2)
            if len(self.frames) < self.frames.maxlen:
                return False
            frames = list(self.frames)
            top = sum(frames[0:3]) / 3
            middle = sum(frames[6:9]) / 3
            bottom = sum(frames[12:15]) / 3
            return top < middle < bottom and bottom - top >= 0.1
