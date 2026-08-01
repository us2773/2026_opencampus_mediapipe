"""条件が一定時間続いたことを判定する状態モジュール。"""

import time


class HoldDetector:
    def __init__(self, duration, clock=time.time):
        self.duration = duration
        self.clock = clock
        self.start_time = None
        self.detected = False
    """#元の関数
    def update(self, condition):
        if not condition:
            self.reset()
            return False
        if self.start_time is None:
            self.start_time = self.clock()
            return False
        self.detected = self.clock() - self.start_time >= self.duration
        return self.detected
    """
    #変更した関数
    def update(self, condition):
        if not condition:
            self.reset()
            return False
        now = self.clock()

        if self.start_time is None:
            self.start_time = now
            return False

        if now - self.start_time >= self.duration:
            self.start_time = now   # 継続判定をリセット
            self.detected = True
            return True

        self.detected = False
        return False

    def reset(self):
        self.start_time = None
        self.detected = False
