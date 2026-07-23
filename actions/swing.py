from collections import deque


class SwingDetector:
    def __init__(self):
        self.frames = deque(maxlen=15)

    def detect(self, landmarks):
        self.frames.append((landmarks[15][1] + landmarks[16][1]) / 2)
        if len(self.frames) < self.frames.maxlen:
            return False
        top = sum(self.frames[0:3]) / 3
        middle = sum(self.frames[6:9]) / 3
        bottom = sum(self.frames[12:15]) / 3
        return top < middle < bottom and bottom - top >= 0.1
