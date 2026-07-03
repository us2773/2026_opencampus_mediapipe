# whileループで撮影処理実行
# 各動作判定がTrueならば、send_command関数を実行

import cv2
import mediapipe as mp
from collections import deque
from datetime import datetime
import action
import client
import csv

mp_pose = mp.solutions.pose          # Pose（全身骨格検出）
mp_hands = mp.solutions.hands        # Hands（手骨格検出）
mp_draw = mp.solutions.drawing_utils # 骨格描画用


# Pose（全身姿勢推定）の設定

pose = mp_pose.Pose(
    static_image_mode=False,         # 動画モード（追跡あり）
    model_complexity=0,              # モデルの複雑さ（0:軽量,1:標準,2:高精度）
    smooth_landmarks=True,           # 座標を平滑化してブレを減らす
    min_detection_confidence=0.5,    # 検出信頼度の閾値
    min_tracking_confidence=0.5      # 追跡信頼度の閾値
)

# Hands（手姿勢推定）の設定

hands = mp_hands.Hands(
    static_image_mode=False,         # 動画モード
    max_num_hands=2,                 # 最大2本の手を検出
    min_detection_confidence=0.5,    # 検出信頼度
    min_tracking_confidence=0.5      # 追跡信頼度
)

# Webカメラを起動
# 0はPC内蔵カメラを表す

cap = cv2.VideoCapture(0)
csv_result = []
header = []

for i in range(32) :
    header.append(f"{i+1}_x")
    header.append(f"{i+1}_y")
    
csv_result.append(header)

floor_y = 0
last_frames = deque(maxlen=25)

# カメラ映像を1フレームずつ処理

count = 0 # フレーム数
action = action.action()
sender = client.client()

while cap.isOpened():
    
    now = datetime.now()
    print("現在時刻:", now) 
    print("ミリ秒:", now.microsecond // 1000)  # microsecondはマイクロ秒（μs）
    count += 1
    # カメラから画像を取得
    ret, frame = cap.read()

    # 画像取得に失敗したら終了
    if not ret:
        break

    # 左右反転（鏡表示）
    frame = cv2.flip(frame, 1)

    # OpenCV(BGR) → MediaPipe(RGB)へ変換
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # PoseとHandsを同じ画像に対して実行
    
    pose_results = pose.process(rgb)
    hands_results = hands.process(rgb)
    
    # Pose（全身骨格）
    
    if pose_results.pose_landmarks:
        # 骨格を画面に描画
        mp_draw.draw_landmarks(
            frame,
            pose_results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS
        )
        landmarks = [] 
        # 33個のランドマークについて座標を取得
        for idx in range(1, 33):
            if idx in range(1, 33) :
                lm = pose_results.pose_landmarks.landmark[idx]

                # 画像サイズ取得
                h, w, _ = frame.shape

                x = lm.x
                y = lm.y

                # ランドマーク番号と座標を表示
            else :
                x = None
                y = None

            landmarks.append(x)
            landmarks.append(y)
        csv_result.append(landmarks) 
            
        #print(f"jump: {action.check_jumping(result[-1])}")
        if action.check_jumping(csv_result[-1]) :
            print("jump")
            sender.send_command("jump")
            
        #print(f"sit: {action.check_sitting(result[-1])}")
        if action.check_sitting(csv_result[-1]) :
            print("sit")
            sender.send_command("sit")
                    
        
        #print(f"tpose_continue: {action.is_tpose(pose_results.pose_landmarks.landmark)}")
        if action.is_tpose(pose_results.pose_landmarks.landmark) :
            print("tpose")
            sender.send_command("tpose")
            
        #print(f"check_tpose: {action.check_tpose(pose_results.pose_landmarks.landmark)}")
        if action.check_tpose(pose_results.pose_landmarks.landmark) :
            print("tpose_continue")
            sender.send_command("tpose_continue")
    # Hands（手骨格）
    
    if hands_results.multi_hand_landmarks:

        # 検出された手の数だけ繰り返す
        for hand_no, hand_landmarks in enumerate(hands_results.multi_hand_landmarks):

            # 手骨格を描画
            mp_draw.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS
            )

            h, w, _ = frame.shape

            # 手は21個のランドマークを持つ
            for idx, lm in enumerate(hand_landmarks.landmark):
                
                x = lm.x
                y = lm.y
                # ランドマーク番号と座標を表示

            if   hands_results.multi_hand_landmarks != None:
                if len(hands_results.multi_hand_landmarks) == 2 :
                    hand1 = hands_results.multi_hand_landmarks[0]
                    hand2 = hands_results.multi_hand_landmarks[1]

                    if action.judge_grab(hand1) or action.judge_grab(hand2):
                        print(f"grab")
                        sender.send_command("grab")
                    #print(f"crap: {action.judge_crap(hand1, hand2)}")
                    if action.judge_crap(hand1, hand2) :
                        print("crap")
                        sender.send_command("crap")
                
    # 結果を表示
    cv2.imshow("Pose + Hands", frame)
    # qキーで終了
    
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# 後処理

# カメラを解放
cap.release()

# ウィンドウを閉じる
cv2.destroyAllWindows()

# MediaPipeのリソースを解放
pose.close()
hands.close()

# 結果のCSV出力（なくてもいい）
with open("result.csv", "w") as f :
    writer = csv.writer(f)
    writer.writerows(csv_result)