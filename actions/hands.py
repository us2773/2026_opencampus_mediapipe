"""手の動作判定。"""

from .geometry import distance
from .check_visibility import check_visibility

def is_grab(hand_landmarks):
    wrist = hand_landmarks.landmark[0]
    pairs = ((5, 8), (9, 12), (13, 16), (17, 20))
    return all(distance(hand_landmarks.landmark[tip], wrist) < distance(hand_landmarks.landmark[base], wrist) for base, tip in pairs)

"""元のやつ
def is_kamehameha(first_hand, second_hand, shoulder_width):
    landmarks = list(first_hand.landmark) +  list(second_hand.landmark)
    if check_visibility(landmarks)  :
        return False 
    th_hands_len = 0.1
    th_wrist_distance = 0.05
    th_wrist_xdiff = 0.1
    th_midf_xdiff = 0.1
    # print(f"shoulder_width: {shoulder_width}")
    
    first_wrist, second_wrist = first_hand.landmark[0], second_hand.landmark[0]
    middle_fingers_extended = (
        distance(first_wrist, first_hand.landmark[12]) > th_hands_len
        and distance(second_wrist, second_hand.landmark[12]) > th_hands_len
    )

    return (
        distance(first_wrist, second_wrist) < th_wrist_distance
        and abs(first_wrist.x - second_wrist.x) < th_wrist_xdiff
        and abs(first_hand.landmark[12].x - second_hand.landmark[12].x) < th_midf_xdiff
        and middle_fingers_extended
    )
"""

#かめはめ波
def is_kamehameha(landmarks):
    left_shoulder = landmarks[11]
    right_shoulder = landmarks[12]
    left_wrist = landmarks[15]
    right_wrist = landmarks[16]
    ratio = 0.4

    # 必要なランドマークが見えているか
    if not check_visibility([
        left_shoulder,
        right_shoulder,
        left_wrist,
        right_wrist
    ]):
        return False

    # 肩幅（正規化用）
    shoulder_width = distance(left_shoulder, right_shoulder)

    # 両手首が近い
    wrists_close = (
        distance(left_wrist, right_wrist)
        < shoulder_width * 0.4
    )

    # 左右の高さがほぼ同じ
    wrists_same_height = (
        abs(left_wrist.y - right_wrist.y)
        < shoulder_width * 0.4
    )

    # 両手が肩より前に出ている
    hands_forward = (
        (left_shoulder.z - left_wrist.z) > 0.45 and
        (right_shoulder.z - right_wrist.z) > 0.45
    )

    return (
        wrists_close
        and wrists_same_height
        and hands_forward
    )

