"""Poseの手のひら中心を使った拍手判定。"""

import time

from .check_visibility import check_visibility
from .geometry import distance, point_xy, get_shoulder_width


class ClapDetector:
    """手のひらが近づき、接触位置で止まったときに拍手を検出する。"""

    def __init__(
        self,
        approach_speed=0.4,
        contact_distance=0.35,
        stop_speed=0.15,
        rebound_speed=0.15,
        approach_hold_seconds=1.0,
        cooldown_seconds=0.2,
        clock=time.monotonic,
    ):
        self._approach_speed = approach_speed
        self._contact_distance = contact_distance
        self._stop_speed = stop_speed
        self._rebound_speed = rebound_speed
        self._approach_hold_seconds = approach_hold_seconds
        self._cooldown_seconds = cooldown_seconds
        self._clock = clock
        self._previous_distance = None
        self._previous_time = None
        self._approach_frames = 0
        self._last_approach_at = None
        self._has_been_close = False
        self._cooldown_until = 0.0
        self.shoulder_width = 0

    def detect(self, landmarks):
        """拍手の接触時に一度だけTrueを返す。"""
        if not check_visibility([landmarks[11], landmarks[12]]):
            self._reset_motion()
            return False

        self.shoulder_width = get_shoulder_width(landmarks)
        now = self._clock()
        current_distance = self._normalized_palm_distance(landmarks)
        if current_distance is None:
            self._reset_motion()
            return False

        if self._previous_distance is None:
            self._store(current_distance, now)
            return False

        elapsed = now - self._previous_time
        if elapsed <= 0:
            self._store(current_distance, now)
            return False

        closing_speed = (self._previous_distance - current_distance) / elapsed
        self._store(current_distance, now)

        if now < self._cooldown_until:
            return False

        if current_distance > 1:
            self._reset_motion()
        elif closing_speed >= self._approach_speed:
            self._approach_frames += 1
            self._last_approach_at = now

        # 最後に速く近づいた時点から一定時間だけ履歴を保持し、その間に接触・停止を確認する。
        if self._last_approach_at is not None and now - self._last_approach_at > self._approach_hold_seconds:
            self._reset_motion()

        is_close_enough = current_distance <= self._contact_distance
        is_stopped = abs(closing_speed) <= self._stop_speed
        has_approached = self._approach_frames >= 2
        if has_approached and is_close_enough:
            self._has_been_close = True

        is_separating_after_close = self._has_been_close and closing_speed <= -self._rebound_speed
        is_contact_stopped = is_close_enough and is_stopped
        if has_approached and (is_contact_stopped or is_separating_after_close):
            self._cooldown_until = now + self._cooldown_seconds
            self._reset_motion()
            return True

        return False

    @staticmethod
    def _palm_center(landmarks, indices):
        points = [point_xy(landmarks[index]) for index in indices]
        return (
            sum(point[0] for point in points) / len(points),
            sum(point[1] for point in points) / len(points),
        )

    def _normalized_palm_distance(self, landmarks):
        shoulder_width = distance(landmarks[11], landmarks[12])
        if shoulder_width == 0:
            return None
        left_palm = self._palm_center(landmarks, (15, 17, 19, 21))
        right_palm = self._palm_center(landmarks, (16, 18, 20, 22))
        return distance(left_palm, right_palm) / shoulder_width

    def _store(self, current_distance, now):
        self._previous_distance = current_distance
        self._previous_time = now

    def _reset_motion(self):
        self._approach_frames = 0
        self._last_approach_at = None
        self._has_been_close = False
