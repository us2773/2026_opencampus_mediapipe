import socket
import cv2
import numpy as np

# 受信側のプログラム
# main.pyと異なるターミナルで起動し、別のウィンドウで映像が流れることを確認

VIDEO_IP = "127.0.0.1"
VIDEO_PORT = 5053

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((VIDEO_IP, VIDEO_PORT))

print(f"Waiting for video on {VIDEO_IP}:{VIDEO_PORT}")

while True:
    data, addr = sock.recvfrom(65535)

    print(f"Received {len(data)} bytes from {addr}")

    buffer = np.frombuffer(data, dtype=np.uint8)
    frame = cv2.imdecode(buffer, cv2.IMREAD_COLOR)

    if frame is None:
        print("Failed to decode JPEG")
        continue

    cv2.imshow("Received Video", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

sock.close()
cv2.destroyAllWindows()