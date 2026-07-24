import socket
import os

import cv2


# 通常のUDP送信上限より余裕を持たせた本番向けの既定値。
# macOSなど上限が低い環境では UDP_MAX_VIDEO_PAYLOAD_SIZE=9000 を指定する。
MAX_VIDEO_PAYLOAD_SIZE = int(os.getenv("UDP_MAX_VIDEO_PAYLOAD_SIZE", "60000"))
JPEG_QUALITIES = (60, 50, 40, 30)


def encode_video_for_udp(frame):
    """UDPで送れるサイズに収まるJPEGへ必要な場合だけ圧縮する。"""
    encoded_frame = frame

    # 通常は既存と同じ品質60で送る。上限を超えた場合だけ品質・解像度を下げる。
    for _ in range(10):
        for quality in JPEG_QUALITIES:
            success, buffer = cv2.imencode(
                ".jpg", encoded_frame, [cv2.IMWRITE_JPEG_QUALITY, quality]
            )
            if not success:
                raise RuntimeError("JPEGへの映像変換に失敗しました")
            if buffer.nbytes <= MAX_VIDEO_PAYLOAD_SIZE:
                return buffer

        height, width = encoded_frame.shape[:2]
        encoded_frame = cv2.resize(
            encoded_frame, (int(width * 0.75), int(height * 0.75)),
            interpolation=cv2.INTER_AREA,
        )

    raise ValueError("UDP送信可能なサイズまで映像を圧縮できませんでした")

class client() :
    def __init__ (self, port) :
        # UDPソケットを作成（参考コードと同じ）
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # 送り先の設定：Unity側と同じIPアドレス・ポート番号にする必要がある
        # 127.0.0.1 = 自分自身（ローカル通信）
        self.serverAddressPort = ("127.0.0.1", port)

    def send_command(self, command):
        """
        コマンド文字列をUnityに送信する関数。
        MediaPipe側でポーズを判定した後、この関数を呼ぶ。
        """
        self.sock.sendto(command.encode(), self.serverAddressPort)
        print(f"送信: {command}")

    def send_video(self, buffer) :
        self.sock.sendto(buffer, self.serverAddressPort)
        # print("send video")
