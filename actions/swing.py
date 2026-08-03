from collections import deque
from .check_visibility import check_visibility
from .geometry import distance, get_shoulder_width
import time

class SwingDetector:
    def __init__(self, cooldown_seconds=0.5):
        self.frames = deque(maxlen=15)
        self.shoulder_frames = deque(maxlen=15)
        self._cooldown_seconds = cooldown_seconds
        self._last_detected_at = 0.0

    def detect(self, landmarks):
        shoulder_width = get_shoulder_width(landmarks)
        th_displacement = 0.1
        th_distance = 0.5 * shoulder_width
        
        left_pinky = landmarks[17]
        right_pinky = landmarks[18]
        left_shoulder = landmarks[11]
        right_shoulder = landmarks[12]
        
        if not check_visibility([left_pinky, right_pinky]) :
            self.frames.clear()
            return False
        else :
            
            if distance(left_pinky, right_pinky) <= th_distance :
                self.frames.append((left_pinky.y + right_pinky.y) / 2)
                self.shoulder_frames.append((left_shoulder.y + right_shoulder.y) / 2)
            else :
                self.frames.clear()
                self.shoulder_frames.clear()
                return False
            
            
            if len(self.frames) < self.frames.maxlen:
                return False
            
            now = time.monotonic() 
                        
            if now - self._last_detected_at < self._cooldown_seconds:
                return False
            
            frames = list(self.frames)
            top = sum(frames[0:3]) / 3
            middle = sum(frames[6:9]) / 3
            bottom = sum(frames[12:15]) / 3
            
            shoulder_frames =  list(self.shoulder_frames)
            swing_start = sum(shoulder_frames[0:3]) / 3
            swing_end = sum(shoulder_frames[12:15]) / 3

            result =  (top < middle < bottom 
                    and bottom - top >= th_displacement
                    and top < swing_start
                    and bottom > swing_end)
            if result :
                self._last_detected_at = now
                self.frames.clear()
                self.shoulder_frames.clear()
            return result
