# 環境

- 動作確認済みOS：Windows
- Python 3.11.9(venv)
- mediapipe 0.10.21
- opencv-python 4.11.0.86

# 環境構築

Pythonバージョンの確認

```powershell
> python -V
Python 3.11.9
```

上記以外のバージョンが表示される場合、Pythonバージョン管理ツールpyenvが入っていない可能性がある。

仮想環境の作成

```powershell
> python -m venv .venv
```

仮想環境のアクティベート

```powershell
> .venv/scripts/activate
```

ライブラリのインストール

```powershell
(.venv)                                                                               
> pip install -r requirements.txt
```

# プログラムの実行

`main.py` を実行するとカメラが立ち上がり、骨格情報が表示される

```powershell
python main.py
```

特定の動作を行うとターミナル上に動作の情報が表示される。また同時にコマンド文字列をUnityに送信する処理が行われる。
