from PySide6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QSizePolicy
from PySide6.QtGui import QPixmap, QPainter, QPen, QColor, QFont
from PySide6.QtCore import Slot, QTimer, Qt, QRect, Signal, QByteArray



from models.model import Model
from models.model import PPEDetectonMode
from controllers.controller import Controller


import os
from dotenv import load_dotenv

from wifi import Cell
import platform
import subprocess
import re



class EnvAccessor():
    device_id = ""
    command_param_file_name = ""


    def __init__(self) :
        load_dotenv()
        self.device_id = os.getenv("DEVICE_ID")
        self.command_param_file_name = os.getenv("COMMAND_PARAMETER_FILE_NAME")

    def get_device_id(self):
        return self.device_id

    def get_command_param_file_name(self):
        return  self.command_param_file_name

        
def run_led_script(light_color:str):

    subprocess.run(["python", "/home/AITRIOS/PPE/app/lled.py", light_color])
    pass

class PPEDemoView(QWidget):       
    def __init__(self, app :QApplication, model :Model, controller :Controller):
        super().__init__()

        self._model = model
        self._controller = controller
        self.env_accessor = EnvAccessor()

        self._model.ppe_detection_mode_changed.connect(self.ppe_detection_mode_changed)

        self.setWindowTitle("安全装備装着確認 Demo")
        

        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        spacer = 20
        half_width = (screen_geometry.width() / 2) - spacer
        print(screen_geometry)

        main_layout = QHBoxLayout()

        # サブのレイアウト(左)
        sub_l_layout = QVBoxLayout()
        self.image_label = InferenceResultImageLabel(r"./views/base.png")
        self.image_label.setScaledContents(True)  # QLabelに合わせて画像をリサイズ

        self.image_label.setFixedWidth(half_width)

        self.image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sub_l_layout.addWidget(self.image_label)


        # サブのレイアウト(右)
        sub_r_layout = QVBoxLayout()


        self.ppe_label = QLabel()
        self.ppe_label = QLabel("安全装備を<br>装着してください")
        self.ppe_label.setStyleSheet("font-size: 96px; color: white; background-color: red;")
        self.ppe_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.ppe_label.setFixedWidth(half_width)
        sub_r_layout.addWidget(self.ppe_label)

        # メインレイアウトに追加
        main_layout.addLayout(sub_l_layout)
        main_layout.addSpacing(spacer)
        main_layout.addLayout(sub_r_layout)

        # メインウィジェットにレイアウトを設定
        self.setLayout(main_layout)


        # 終了イベントの処理を設定
        app.aboutToQuit.connect(self.on_exit)

        # 自動でコマンドパラメータのIPアドレスを更新
        self._controller.set_config_host(self.env_accessor.get_command_param_file_name())
        
        # 自動で推論を開始
        self._controller.start_inference(self.env_accessor.get_device_id())
        self.timer_proc()


    # タイマー制御
    def timer_proc(self):
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.interval_timer)
        self.timer.start()

    def interval_timer(self):
        self.draw_main_mode()              
        self._controller.get_inference_result(self.env_accessor.get_device_id())        


    # 人数カウントの更新通知を受信
    @Slot(int)
    def ppe_detection_mode_changed(self, value: PPEDetectonMode):
        self._ppe_detection_mode = value        
        self.draw_main_mode()              

    _ppe_detection_mode = PPEDetectonMode.NOT_EQ

    def draw_main_mode(self):
        match self._ppe_detection_mode:
            case PPEDetectonMode.ALL_EQ: # 全装備着装
                self.ppe_label.setText("作業開始<br>してください")
                self.ppe_label.setStyleSheet("font-size: 96px; color: black; background-color: green;")
                run_led_script("G")      
            case PPEDetectonMode.NOT_FULLY_EQ: # 着装未完全
                self.ppe_label.setText("一部未装着です")
                self.ppe_label.setStyleSheet("font-size: 96px; color: black; background-color: yellow;")
                run_led_script("Y")
            case PPEDetectonMode.NOT_EQ: # 装備未着装
                self.ppe_label.setText("安全装備を<br>装着してください")
                self.ppe_label.setStyleSheet("font-size: 96px; color: white; background-color: red;")
                run_led_script("R")

    @Slot()
    def on_exit(self):
        print("アプリケーションが終了されました。")
        run_led_script("N")
        # 自動で推論を終了
        self._controller.stop_inference(self.env_accessor.get_device_id())


# 推論結果を表示するイメージラベル
class InferenceResultImageLabel(QLabel):
    def __init__(self, image_path):
        super().__init__()
        self.pixmap = QPixmap(image_path)
        self.setPixmap(self.pixmap)
        self.inference_results = []  # 四角形のリスト

    def add_inference_result(self, rect: QRect):
        print("append")
        self.inference_results.append(rect)
        self.update()  # 再描画

    def clear_inference_result(self):
        print("clear")
        self.inference_results.clear()
        self.inference_results = []  # 四角形のリスト
        self.update()  # 再描画

    def paintEvent(self, event):
        super().paintEvent(event)
        self.setPixmap(self.pixmap)
        
        painter = QPainter(self)
        pen = QPen(QColor(255, 0, 0), 2, Qt.PenStyle.SolidLine)

        painter.setPen(pen)
        font = QFont("Arial", 24)
        painter.setFont(font)

        for rect in self.inference_results:
            print("paint")
            print(rect)

            painter.drawRect(rect)
            painter.drawText(rect.x() + 10, rect.y() + 20, f"{rect.x()},{rect.y()},{rect.width()},{rect.height()}")