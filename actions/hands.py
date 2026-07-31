"""手の動作判定。"""

from .geometry import distance


def is_grab(hand_landmarks):
    wrist = hand_landmarks.landmark[0]
    pairs = ((5, 8), (9, 12), (13, 16), (17, 20))
    return all(distance(hand_landmarks.landmark[tip], wrist) < distance(hand_landmarks.landmark[base], wrist) for base, tip in pairs)


def is_kamehameha(first_hand, second_hand, shoulder_width):
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
