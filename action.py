from collections import deque
import time
import math

class action() :
    def __init__(self) :
        self._last_frames: deque = deque(maxlen=25)
        self._tpose_start_time = None #時間のための変数，Tポーズを始めた時刻
        self._tpose_detected = False #Tポーズを認識したかどうかの変数，最初は認識してないからFalse
        #　追加
        self._surprise_start_time = None #時間のための変数，驚かしポーズを始めた時刻
        self._surprise_detected = False #驚かしポーズを認識したかどうかの変数，最初は認識してないからFalse
        #追加
        self._message = {"surprise": False}#"Kick": False}#"jump": False, "sit": False, "crap": False, "grab": False, "tpose": False, "surprise": False}
    
    @property
    def last_frames(self) :
        return self._last_frames
    
    @property
    def message(self) :
        return self._message
    
    @property
    def tpose_start_time(self) :
        return self._tpose_start_time
    
    @property
    def tpose_detected(self) :
        return self._tpose_detected
    
    @property #追加
    def surprise_start_time(self):
        return self._surprise_start_time

    @property #追加
    def surprise_detected(self):
        return self._surprise_detected
    
    def update_tpose_start_time(self, v) :
        self._tpose_start_time = v
        
    def update_topse_detected(self, v) :
        self._tpose_detected = v

    #追加    
    def update_surprise_start_time(self, v):
        self._surprise_start_time = v

    #追加
    def update_surprise_detected(self, v):
        self._surprise_detected = v   
    
    def add_que(self, frame) :
        self._last_frames.append(frame)

    def check_jumping(self, now_frame) :
        left_hip = now_frame[45]
        #self.last_frames.append(left_hip)
        self.add_que(left_hip)
        if len(self.last_frames) == 25 :
            
            left_foot = (self.last_frames[0]+ self.last_frames[1]+ self.last_frames[2]) / 3
            left_side = (self.last_frames[5]+ self.last_frames[6]+ self.last_frames[7]) / 3
            top =  (self.last_frames[10]+ self.last_frames[11]+ self.last_frames[12]) / 3
            right_side = (self.last_frames[15]+ self.last_frames[16]+ self.last_frames[17]) / 3
            right_foot = (self.last_frames[20]+ self.last_frames[21]+ self.last_frames[22]) / 3
            if (left_foot > left_side and left_side > top and top < right_side and right_side < right_foot and left_foot - top >= 0.05) :
                return True
            else :
                return False
        else :
            return False
        
    def check_sitting(self, now_frame): 
        left_hip = now_frame[45]
        right_hip = now_frame[47]
        left_knee = now_frame[49]
        right_knee = now_frame[51]
        
        if left_hip > left_knee and right_hip > right_knee :
            return True
        else :
            return False
    
    def calc_angle(self, a, b, c):
        """
        a, b, c : (x, y)
        bを頂点とした角度を返す
        """
        #ベクトル
        ba = (a[0] - b[0], a[1] - b[1])
        bc = (c[0] - b[0], c[1] - b[1])
        #内積
        dot = ba[0] * bc[0] + ba[1] * bc[1]
        #ベクトルの長さ
        norm_ba = math.sqrt(ba[0]**2 + ba[1]**2)
        norm_bc = math.sqrt(bc[0]**2 + bc[1]**2)
        #cosθ=内積/|ba||bc|
        cos_theta = dot / (norm_ba * norm_bc)

        # 誤差対策(1.00000001と-1.00000001になることがあるらしくそれを防ぐ)
        cos_theta = max(-1.0, min(1.0, cos_theta))
        #acosでθを求める，acos(cos_theta)はラジアン(π/2など)で返すためmath.degrees()で度数法(90°など)に変換
        angle = math.degrees(math.acos(cos_theta))

        return angle

    # 肩，肘角度のためのランドマークについて
    def check_tpose(self, landmarks):
        # 左
        left_shoulder = (landmarks[11].x, landmarks[11].y)
        left_elbow = (landmarks[13].x, landmarks[13].y)
        left_hip = (landmarks[23].x, landmarks[23].y)
        left_wrist = (landmarks[15].x, landmarks[15].y)
        # 右
        right_shoulder = (landmarks[12].x, landmarks[12].y)
        right_elbow = (landmarks[14].x, landmarks[14].y)
        right_hip = (landmarks[24].x, landmarks[24].y)
        right_wrist = (landmarks[16].x, landmarks[16].y)
        # 肩角度を計算
        left_shoulder_angle = self.calc_angle(left_elbow, left_shoulder, left_hip)
        right_shoulder_angle = self.calc_angle(right_elbow, right_shoulder, right_hip)
        # 肘角度を計算
        left_elbow_angle = self.calc_angle(left_shoulder, left_elbow, left_wrist)
        right_elbow_angle = self.calc_angle(right_shoulder, right_elbow, right_wrist)
        # 角度表示
        return (
            80 <= left_shoulder_angle <= 100 and
            80 <= right_shoulder_angle <= 100 and
            150 <= left_elbow_angle <= 180 and
            150 <= right_elbow_angle <= 180
        )
        
    def is_tpose(self, landmarks) :
            # T字判定（6/30追加）
            
        if self.check_tpose(landmarks):

            # Tポーズ開始時刻を記録
            if self.tpose_start_time is None:
                # tpose_start_time = time.time() #開始時刻を保存
                self.update_tpose_start_time(time.time())
                return False

            # 3秒以上維持したら認識
            elif time.time() - self.tpose_start_time >= 1: #開始時間と維持を続けた時の現在時間を比較
                self.update_topse_detected(True)
                return True
        else:
            # 条件を外れたらリセット
            #tpose_start_time = None
            self.update_tpose_start_time(None)
            #tpose_detected = False
            self.update_topse_detected(False)
            return False

    #追加    
    def check_surprise(self, landmarks):
        # 左
        left_shoulder = (landmarks[11].x, landmarks[11].y)
        left_elbow = (landmarks[13].x, landmarks[13].y)
        left_hip = (landmarks[23].x, landmarks[23].y)
        left_wrist = (landmarks[15].x, landmarks[15].y)

        # 右
        right_shoulder = (landmarks[12].x, landmarks[12].y)
        right_elbow = (landmarks[14].x, landmarks[14].y)
        right_hip = (landmarks[24].x, landmarks[24].y)
        right_wrist = (landmarks[16].x, landmarks[16].y)

        # 肩角度を計算
        left_shoulder_angle = self.calc_angle(left_elbow, left_shoulder, left_hip)
        right_shoulder_angle = self.calc_angle(right_elbow, right_shoulder, right_hip)

        # 肘角度を計算 
        left_elbow_angle = self.calc_angle(left_shoulder, left_elbow, left_wrist)
        right_elbow_angle = self.calc_angle(right_shoulder, right_elbow, right_wrist)

        # 肩幅
        shoulder_width = abs(right_shoulder[0] - left_shoulder[0])

        # 手首間距離
        wrist_width = abs(right_wrist[0] - left_wrist[0])

        # デバッグ用（必要なら）
        # print(f"L肩:{left_shoulder_angle:.1f}, R肩:{right_shoulder_angle:.1f}")
        # print(f"L肘:{left_elbow_angle:.1f}, R肘:{right_elbow_angle:.1f}")
        # print(f"肩幅:{shoulder_width:.3f}, 手首間:{wrist_width:.3f}")

        return (
            120 <= left_shoulder_angle <= 170 and
            120 <= right_shoulder_angle <= 170 and
            120 <= left_elbow_angle <= 180 and
            120 <= right_elbow_angle <= 180 and
            wrist_width > shoulder_width #両手首の距離が肩幅より大きい
        ) 

#追加
    def is_surprise(self, landmarks):

        # 驚かしポーズ判定
        if self.check_surprise(landmarks):

            # 開始時刻を記録
            if self.surprise_start_time is None:
                self.update_surprise_start_time(time.time())
                return False

            # 1秒以上維持したら認識
            elif time.time() - self.surprise_start_time >= 1:
                self.update_surprise_detected(True)
                return True

        else:
            # 条件を外れたらリセット
            self.update_surprise_start_time(None)
            self.update_surprise_detected(False)
            return False

    # 2点間の距離
    def distance(self, p1, p2):
        return math.sqrt(
            (p1.x - p2.x) ** 2 +
            (p1.y - p2.y) ** 2
        )
        
    def judge_crap(self, hand1, hand2):
                    
        hand_distance = self.distance(
            hand1.landmark[12],
            hand2.landmark[12]
        )

        # しきい値
        if hand_distance < 0.10:
            return True
        else :
            return False

    #追加キック(右足なら左斜め前にける，左足なら右斜め前にける)
    def check_kick(self, landmarks):
        # 左
        left_hip = (landmarks[23].x, landmarks[23].y)
        left_knee = (landmarks[25].x,landmarks[25].y)
        left_ankle = (landmarks[27].x,landmarks[27].y)

        # 右
        right_hip = (landmarks[24].x,landmarks[24].y)
        right_knee = (landmarks[26].x, landmarks[26].y)
        right_ankle = (landmarks[28].x, landmarks[28].y)

        # 膝角度
        left_knee_angle = self.calc_angle(left_hip, left_knee, left_ankle)
        right_knee_angle = self.calc_angle(right_hip, right_knee, right_ankle)

        # 左足
        left_to_left = self.distance(landmarks[23], landmarks[27])
        right_to_left = self.distance(landmarks[24], landmarks[27])

        # 右足
        right_to_right = self.distance(landmarks[24], landmarks[28])
        left_to_right = self.distance(landmarks[23], landmarks[28])

        if (
            left_knee_angle > 155 and
            left_to_left > right_to_left     #左膝と左足首の距離が右膝と左足首の距離より大きい
        ) or (
            right_knee_angle > 155 and
            right_to_right > left_to_right   #右膝と右足首の距離が左膝と右足首の距離より大きい
        ):
            return True
        else:
            return False

    #「掴む」を判定する関数
    def judge_grab(self, hand_landmarks):
        wrist = hand_landmarks.landmark[0]

        base_tip_pairs = [
        (5, 8),
        (9, 12),
        (13, 16),
        (17, 20)
        ]

        count = 0

        for base_idx, tip_idx in base_tip_pairs:
            base = hand_landmarks.landmark[base_idx]
            tip = hand_landmarks.landmark[tip_idx]

            base_wrist_distance = self.distance(wrist, base)
            tip_wrist_distance = self.distance(wrist, tip)

            if tip_wrist_distance < base_wrist_distance:
                count += 1
        
        return count == 4
    
    def change_message(self, message: str) :
        if (message in self.message) :
            self.message[message] = True
    
    def reset_message(self) :
        #self._message = {"jump": False, "sit": False, "crap": False, "grab": False, "tpose": False}
        for key, _ in self.message.items() :
            self.message[key] = False

