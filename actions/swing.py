from collections import deque
from .check_visibility import check_visibility

class SwingDetector:
    def __init__(self):
        self.frames = deque(maxlen=15)
        self.shoulder_frames = deque(maxlen=15)

    def detect(self, landmarks):
        th = 0.1
        if not check_visibility([landmarks[15], landmarks[16]]) :
            self.frames.clear()
            return False
        else :
            left_wrist = landmarks[15].y
            right_wrist = landmarks[16].y
            left_shoulder = landmarks[11].y
            right_shoulder = landmarks[12].y
            
            self.frames.append((left_wrist + right_wrist) / 2)
            self.shoulder_frames.append((left_shoulder + right_shoulder) / 2)
            
            
            if len(self.frames) < self.frames.maxlen:
                return False
            frames = list(self.frames)
            top = sum(frames[0:3]) / 3
            middle = sum(frames[6:9]) / 3
            bottom = sum(frames[12:15]) / 3
            
            shoulder_frames =  list(self.shoulder_frames)
            swing_start = sum(shoulder_frames[0:3]) / 3
            swing_end = sum(shoulder_frames[12:15]) / 3
            """
            print(f"top < middle < bottom: {top < middle < bottom}")
            print(f"bottom - top >= th: {bottom - top >= th}")
            print(f"top < swing_start: {top < swing_start}")
            print(f"bottom > swing_end: {bottom > swing_end}")
            """
            return (top < middle < bottom 
                    and bottom - top >= th
                    and top < swing_start
                    and bottom > swing_end)
