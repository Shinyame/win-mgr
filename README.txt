【Windows Shutdown - ビルド手順】

1. 必要なPythonパッケージをインストール
----------------------------------
Python 3.x がインストールされていることを確認し、以下のコマンドを実行：

pip install pyinstaller psutil

2. EXEファイルを作成
--------------------------
次のコマンドを PowerShell または cmd で実行：

pyinstaller --noconsole --onefile mgr-app.py

3. 出力ファイル
--------------------------
dist/mgr-app.exe に出力されます。

4. 実行時の注意
--------------------------
- 実行には管理者権限が必要な場合があります。
- shutdown_info.json に最後のシャットダウン日時が記録されます。

【アイコンファイルについて】

- あとでやる。
