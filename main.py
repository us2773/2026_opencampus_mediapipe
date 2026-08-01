# whileループで撮影処理実行
# 各動作判定がTrueならば、send_command関数を実行

import cv2
import mediapipe as mp
from collections import deque
from datetime import datetime
import action
import client
import csv
from actions.geometry import get_shoulder_width


def send_message(messages: dict, sender: client.client) : 
    for key, value in messages.items() :
        if (value) :
            sender.send_command(key)

    if not any(messages.values()) :
        sender.send_command("default")
    
def main(cap: cv2.VideoCapture) : 
    
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

    

    # CSV書き込み用
    all_landmarks = []
    header = []

    for i in range(32) :
        header.append(f"{i+1}_x")
        header.append(f"{i+1}_y")
    action_judge = action.action()
    action_sender = client.client(5052)
    video_sender = client.client(5053)   
    
    print(cap.isOpened)
    while cap.isOpened():
        shoulder_width = 0
        now = datetime.now()
        #print("現在時刻:", now) 
        #print("ミリ秒:", now.microsecond // 1000)  # microsecondはマイクロ秒（μs）
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
                    

                landmarks.append([x,y])
            all_landmarks.append(landmarks) 
            
            video_txt = "default"
            last_landmarks = pose_results.pose_landmarks.landmark
            if action_judge.check_jumping(last_landmarks) :
                action_judge.change_message("jump")
                video_txt = "jump"
                
            if action_judge.judge_swing(last_landmarks) :
                action_judge.change_message("swing")
                video_txt = "swing"

            if action_judge.judge_uppercut(last_landmarks) :
                action_judge.change_message("upper")
                video_txt = "upper"

            if action_judge.judge_clap(last_landmarks) :
                action_judge.change_message("clap")
                video_txt = "clap"
            
            if action_judge.continue_sit(last_landmarks) :
                action_judge.change_message("sit_continue")
                video_txt = "sit_continue"

            if action_judge.is_closs_arms(last_landmarks): 
                action_judge.change_message("closs_continue")
                video_txt = "closs_continue"
                
            if action_judge.is_tpose(last_landmarks) :
                action_judge.change_message("tpose_continue")
                video_txt = "tpose_continue"
                
            if action_judge.is_surprise(last_landmarks):
                action_judge.change_message("surprise_continue")
                video_txt = "surprise"
                
            if action_judge.check_kick(last_landmarks):
                action_judge.change_message("Kick")
                video_txt = "kick"
                
            shoulder_width = get_shoulder_width(last_landmarks)
            
            print(video_txt)


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
                
                if hands_results.multi_hand_landmarks != None:
                    if len(hands_results.multi_hand_landmarks) == 2 :
                        hand1 = hands_results.multi_hand_landmarks[0]
                        hand2 = hands_results.multi_hand_landmarks[1]

                        if action_judge.judge_grab(hand1) or action_judge.judge_grab(hand2):
                            action_judge.change_message("grab")
                            video_txt = "grab"
                            
                        
                        if action_judge.is_kamehameha(hand1, hand2, shoulder_width) :
                            action_judge.change_message("kamehameha_continue")
                            video_txt = "kamehameha"
                            
                """
                        if action_judge.judge_kamehameha(hand1, hand2, shoulder_width) :
                            action_judge.change_message("kamehameha")
                """
        cv2.putText(frame,
        text=f'{video_txt}',
        org=(100, 100),
        fontFace=cv2.FONT_HERSHEY_SIMPLEX,
        fontScale=1.0,
        color=(0, 255, 0),
        thickness=2,
        lineType=cv2.LINE_4)
        send_message(action_judge.message, action_sender)
        # print(action.message)
        action_judge.reset_message()

        buffer = client.encode_video_for_udp(frame)
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

if __name__ == "__main__" :
    cap = cv2.VideoCapture(0)
    main(cap)