"""単発の全身ポーズ判定。"""

import math

from .geometry import angle, distance, point_xy, segment_distance
from .check_visibility import check_visibility

def is_sitting(landmarks):
    if not check_visibility([landmarks[23], landmarks[24], landmarks[25], landmarks[26]]) :
        return False
    else :
        return landmarks[23].y > landmarks[25].y and landmarks[24].y > landmarks[26].y


def is_tpose(landmarks):
        left_shoulder, right_shoulder = landmarks[11], landmarks[12]
        left_elbow, right_elbow = landmarks[13], landmarks[14]
        left_wrist, right_wrist = landmarks[15], landmarks[16]
        left_hip, right_hip = landmarks[23], landmarks[24]
        if not check_visibility([left_shoulder, right_shoulder, 
                                left_elbow, right_elbow,
                                left_wrist, right_wrist,
                                left_hip, right_hip]) :
            return False
        else :
            return (80 <= angle(left_elbow, left_shoulder, left_hip) <= 100 and
                80 <= angle(right_elbow, right_shoulder, right_hip) <= 100 and
                150 <= angle(left_shoulder, left_elbow, left_wrist) <= 180 and
                150 <= angle(right_shoulder, right_elbow, right_wrist) <= 180)


def is_surprise(landmarks):
    
    left_shoulder, right_shoulder = landmarks[11], landmarks[12]
    left_elbow, right_elbow = landmarks[13], landmarks[14]
    left_wrist, right_wrist = landmarks[15], landmarks[16]
    left_hip, right_hip = landmarks[23], landmarks[24]
    shoulder_width = abs(point_xy(right_shoulder)[0] - point_xy(left_shoulder)[0])
    wrist_width = abs(point_xy(right_wrist)[0] - point_xy(left_wrist)[0])
    
    if not check_visibility([left_shoulder, right_shoulder, 
                                left_elbow, right_elbow,
                                left_wrist, right_wrist,
                                left_hip, right_hip]) :
            return False
    else :
        return (120 <= angle(left_elbow, left_shoulder, left_hip) <= 170 and
            120 <= angle(right_elbow, right_shoulder, right_hip) <= 170 and
            120 <= angle(left_shoulder, left_elbow, left_wrist) <= 180 and
            120 <= angle(right_shoulder, right_elbow, right_wrist) <= 180 and
            wrist_width > shoulder_width)


def is_kick(landmarks):
    left_hip, right_hip = landmarks[23], landmarks[24]
    left_knee, right_knee = landmarks[25], landmarks[26]
    left_ankle, right_ankle = landmarks[27], landmarks[28]
    if not check_visibility([left_hip, right_hip, 
                            left_knee, right_knee, 
                            left_ankle, right_ankle]) :
            return False
    else :
        return ((angle(left_hip, left_knee, left_ankle) > 155 and distance(left_hip, left_ankle) > distance(right_hip, left_ankle)) or
            (angle(right_hip, right_knee, right_ankle) > 155 and distance(right_hip, right_ankle) > distance(left_hip, right_ankle)))


def is_crossed_arms(landmarks):
    if not check_visibility(landmarks[13:16]) :
            return False
    else :
        left_elbow = [landmarks[13].x, landmarks[13].y]
        right_elbow = [landmarks[14].x, landmarks[14].y]
        left_wrist = [landmarks[15].x, landmarks[15].y]
        right_wrist = [landmarks[16].x, landmarks[16].y]
        
        left_x, left_y = point_xy(left_elbow)
        left_wrist_x, left_wrist_y = point_xy(left_wrist)
        right_x, right_y = point_xy(right_elbow)
        right_wrist_x, right_wrist_y = point_xy(right_wrist)
        
        left_angle = math.degrees(math.atan2(left_wrist_y - left_y, left_wrist_x - left_x))
        right_angle = math.degrees(math.atan2(right_wrist_y - right_y, right_wrist_x - right_x))
        
        horizontal = lambda value: abs(value) <= 30 or abs(abs(value) - 180) <= 30
        vertical = lambda value: abs(abs(value) - 90) <= 30
        return segment_distance(left_elbow, left_wrist, right_elbow, right_wrist) <= 0.1 and ((horizontal(left_angle) and vertical(right_angle)) or (horizontal(right_angle) and vertical(left_angle)))
