from collections import deque
from .check_visibility import check_visibility
from .geometry import get_shoulder_width
import time 

class JumpDetector:
    def __init__(self, cooldown_seconds=0.5):
        self.maxlen = 11
        self.frames_left = deque(maxlen=self.maxlen)
        self.frames_right = deque(maxlen=self.maxlen)
        self.frames_z = deque(maxlen=self.maxlen)
        self._cooldown_seconds = cooldown_seconds
        self._last_detected_at = 0.0

    def detect(self, landmarks):
        shoulder_width = get_shoulder_width(landmarks)
        th = shoulder_width * 0.5
        left_ankle = landmarks[27]
        right_ankle = landmarks[28]
        if not check_visibility([left_ankle, right_ankle]) :
            self.frames_left.clear()
            self.frames_right.clear()
            self.frames_z.clear()
            return False
        else :
            self.frames_left.append(left_ankle.y)
            self.frames_right.append(right_ankle.y)
            self.frames_z.append(right_ankle.z)
            
            if len(self.frames_left) < self.frames_left.maxlen :
                return False
            
            now = time.monotonic() 
            
            if now - self._last_detected_at < self._cooldown_seconds:
                return False
                
            is_jump_l = self.check_jump_waveform(self.frames_left, th)
            is_jump_r = self.check_jump_waveform(self.frames_right, th)
            is_const_camera_distance = self.isconst_camera_distance(self.frames_z)
            
            result = is_jump_l and is_jump_r and is_const_camera_distance
            if  result:
                self._last_detected_at = now
                self.frames_left.clear()
                self.frames_right.clear()
                self.frames_z.clear()
                return result
                        
    def check_jump_waveform(self, frames, th) :
        frames = list(frames)
        left_foot = sum(frames[0:2]) / 2
        left_side = sum(frames[2:4]) / 2
        top = sum(frames[4:6]) / 2
        right_side = sum(frames[6:8]) / 2
        right_foot = sum(frames[8:10]) / 2
        return (left_foot > left_side > top < right_side < right_foot and left_foot - top >= th)
    
    def isconst_camera_distance(self, frames) :
        frames = list(frames)
        variation = max(frames) - min(frames)
        return variation < 0.4