"""手の動作判定。"""

from .geometry import distance
from .check_visibility import check_visibility

def is_grab(hand_landmarks):
    wrist = hand_landmarks.landmark[0]
    pairs = ((5, 8), (9, 12), (13, 16), (17, 20))
    return all(distance(hand_landmarks.landmark[tip], wrist) < distance(hand_landmarks.landmark[base], wrist) for base, tip in pairs)


#かめはめ波
def is_kamehameha(landmarks):
    left_shoulder = landmarks[11]
    right_shoulder = landmarks[12]
    left_wrist = landmarks[15]
    right_wrist = landmarks[16]
    ratio1 = 0.4 #肩幅の閾値変更用(両手首の距離)
    ratio2 = 0.4 #肩幅での閾値変更用(左右の手首の高さ)
    ratio3 = 0.5 #肩幅と手首のz座標の差の絶対値変更用

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
        < shoulder_width * ratio1
    )
    # 左右の高さがほぼ同じ
    wrists_same_height = (
        abs(left_wrist.y - right_wrist.y)
        < shoulder_width * ratio2
    )
    # 両手が肩より前に出ている
    hands_forward = (
        (left_shoulder.z - left_wrist.z) > ratio3 and
        (right_shoulder.z - right_wrist.z) > ratio3
    )
    return (
        wrists_close
        and wrists_same_height
        and hands_forward
    )