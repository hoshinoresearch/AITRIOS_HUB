# What is AITRIOS_HUB/ AITRIOS HUBとは 
To easy integrate AITRIOS that is edge AI sensing device, for any device and cloud service.
(This service is not an official service provided by SONY.)

SONY製エッジAIセンシングデバイス「
AITRIOS」を非常に簡単に、他のものと連携できるHUBサービス。
(本サービスはSONYが提供するオフィシャルなサービスではありません。)

# Structure of AITRIOS_HUB AITRIOS_HUBの構成要素
server部分とhub app部分で構成されています。
また、AITRIOS HUBはPythonで実装されているため、PCやRaspberry Piなど、Pythonが稼働する環境で実行することができます。

## server
AITRIOSのConsoleサービスが提供するRest API(以下のURLはリファレンス)をアプリで利用しやすくまとめ、推論結果をデシリアライズした形でローカルRDB(SQLite)に蓄積し、Fast APIでAPI利用できる仕組みを提供します。<br/>
https://developer.aitrios.sony-semicon.com/edge-ai-sensing/documents/console-rest-api-specification/

### AITRIOS_HUB.py
AITRIOS HUBのクライアントアプリから呼び出されるFastAPIで構築されたWeb API

### AITRIOSLocalDBHandler.py
SQLiteを用いて、推論結果の保存と読み出しを行う

### ConsoleWrapperLimited.py
アプリからの利用頻度が高いConsole Rest APIを呼び出すためのWeb API Proxy

### Desilialize.py
flatbuffersを用いて、推論結果をデシリアライズする

### セットアップ方法
以下のライブラリをインストールする
pip install fastapi
pip install requests
pip install numpy
pip install opencv-python
pip install flatbuffers
pip install uvicorn
pip install python-dotenv

### 起動方法
uvicornでサーバーを起動
uvicorn AITRIOS_Hub:app_ins --reload --host XXX.XXX.XXX.XXX --port 8080 --no-access-log


## hub app
GUIライブラリにPySide6を用いたAITRIOS対応のエッジAI センシングデバイスのセットアップおよび推論結果の確認ができるアプリ。<br/>
現在は、以下の機能が提供されています。<br/>
①セットアップ用QRコード表示<br/>
②デバイスIDとコマンドパラメータ名登録<br/>
③CROPPING設定<br/>
④ローカルサーバーアドレス設定<br/>
⑤推論開始と終了<br/>
本アプリを参考に、MVCの設計パターンに基づく、AITRIOSアプリケーションを作ることができる。

### controllers
AITRIOS HUBが提供するWeb APIと連携することができる処理を実装しています。<br/>
自デバイスがuvicornにてホストしているサーバーアドレスに接続しに行くため、クライアントとサーバーが分かれている場合はget_base_urlメソッドを変更してください。

### models
推論結果を保持しています。

### views
モニタリング画面、各種設定画面を実装しています。

### セットアップ方法
serverに加え、以下のライブラリをインストールする
pip install PySide6
pip install wifi
pip install Rpi.GPIO

### 起動方法
python aitrios_hub_demo.py

# ユースケース対応サンプルアプリ
## CongestionDetection
混雑検知

## LockoutDetection
危険領域侵入検知

## PPE
安全装備装着確認
