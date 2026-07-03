import socket

class client() :
    def __init__ (self) :
        # UDPソケットを作成（参考コードと同じ）
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # 送り先の設定：Unity側と同じIPアドレス・ポート番号にする必要がある
        # 127.0.0.1 = 自分自身（ローカル通信）
        # 5052      = ポート番号（Unity側のUDPReceive.csと合わせる）
        self.serverAddressPort = ("127.0.0.1", 5052)

    def send_command(self, command):
        """
        コマンド文字列をUnityに送信する関数。
        MediaPipe側でポーズを判定した後、この関数を呼ぶ。
        """
        self.sock.sendto(command.encode(), self.serverAddressPort)
        print(f"送信: {command}")
