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
    model_complexity=2,              # モデルの複雑さ（0:軽量,1:標準,2:高精度）
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
all_landmarks = []
header = []

for i in range(32) :
    header.append(f"{i+1}_x")
    header.append(f"{i+1}_y")
    
# csv_result.append(header)

floor_y = 0
last_frames = deque(maxlen=25)

# カメラ映像を1フレームずつ処理

count = 0 # フレーム数
action = action.action()
action_sender = client.client(5052)
video_sender = client.client(5053)

def send_message(messages: dict) : 
    for key, value in messages.items() :
        if (value) :
            action_sender.send_command(key)
    if not any(messages.values()) :
        action_sender.send_command("default")

while cap.isOpened():
    
    now = datetime.now()
    #print("現在時刻:", now) 
    #print("ミリ秒:", now.microsecond // 1000)  # microsecondはマイクロ秒（μs）
    count += 1
    # カメラから画像を取得
    ret, frame = cap.read()

    # 画像取得に失敗したら終了
    if not ret:
        break

    # 左右反転（鏡表示）
    # frame = cv2.flip(frame, 1)

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
        for idx in range(0, 33):
            if idx in range(0, 33) :
                lm = pose_results.pose_landmarks.landmark[idx]

                # 画像サイズ取得
                h, w, _ = frame.shape

                x = lm.x
                y = lm.y

                # ランドマーク番号と座標を表示
            else :
                x = None
                y = None

            #landmarks.append(x)
            #landmarks.append(y)
            landmarks.append([x,y])
        all_landmarks.append(landmarks) 

        print_idx = 31
        p = all_landmarks[-1][print_idx]

        cv2.circle(
            frame,
            (int(p[0] * w), int(p[1] * h)),
            8,
            (0, 0, 255),
            -1
        )

        cv2.putText(
            frame,
            f"{print_idx}",
            (int(p[0] * w) + 10, int(p[1] * h)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 0, 255),
            2
        )
            
        if action.check_jumping(all_landmarks[-1]) :
            action.change_message("jump")
            
        if action.judge_swing(all_landmarks[-1]) :
            action.change_message("swing")
            
        if action.check_sitting(all_landmarks[-1]) :
            action.change_message("sit")
        
        if action.judge_closs_arms(all_landmarks[-1]) :
            action.change_message("closs")
        
        if action.is_tpose(pose_results.pose_landmarks.landmark) :
            action.change_message("tpose")
            
        if action.check_tpose(pose_results.pose_landmarks.landmark) :
            action.change_message("tpose_continue")

        #追加
        if action.is_surprise(pose_results.pose_landmarks.landmark):
            action.change_message("surprise")

        if action.check_surprise(pose_results.pose_landmarks.landmark):
            action.change_message("surprise_continue")

        if action.check_kick(pose_results.pose_landmarks.landmark):
            action.change_message("Kick")

    # Hands（手骨格）
    
    if hands_results.multi_hand_landmarks:

        # 検出された手の数だけ繰り返す
        for hand_no, hand_landmarks in enumerate(hands_results.multi_hand_landmarks):

            # 手骨格を描画
            """
            mp_draw.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS
            )
            """
            h, w, _ = frame.shape

            # 手は21個のランドマークを持つ
            for idx, lm in enumerate(hand_landmarks.landmark):
                
                x = lm.x
                y = lm.y
                # ランドマーク番号と座標を表示

            if hands_results.multi_hand_landmarks != None:
                if len(hands_results.multi_hand_landmarks) == 2 :
                    hand1 = hands_results.multi_hand_landmarks[0]
                    hand2 = hands_results.multi_hand_landmarks[1]

                    if action.judge_grab(hand1) or action.judge_grab(hand2):
                        action.change_message("grab")
                    if action.judge_crap(hand1, hand2) :
                        action.change_message("crap")

                        print("crap")
                        action.change_message("crap")

                    if action.is_kamehameha(hand1, hand2) :
                        print("kamehameha")
                        action.change_message("kamehameha")
            
                    if action.judge_kamehameha(hand1, hand2) :
                        print("kamehameha_continue")
                        action.change_message("kamehameha_continue")
    send_message(action.message)
    print(action.message)
    action.reset_message()

    _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 60])
    video_sender.send_video(buffer)
                
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
    writer.writerows(all_landmarks)