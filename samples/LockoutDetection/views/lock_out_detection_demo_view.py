from PySide6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QSizePolicy
from PySide6.QtGui import QPixmap, QPainter, QPen, QColor, QFont, QKeyEvent
from PySide6.QtCore import Slot, QTimer, Qt, QRect, Signal, QByteArray

from models.model import Model
from controllers.controller import Controller


import os
from dotenv import load_dotenv
from wifi import Cell


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


import multiprocessing
import subprocess

def run_led_script():
    subprocess.run(["python", "/home/raspi/AITRIOS/LockOutDetectionDemoView/app/lled.py"])

class LockOutDetectionDemoView(QWidget):       
    def __init__(self, app :QApplication, model :Model, controller :Controller):
        super().__init__()

        self._model = model
        self._controller = controller
        self.env_accessor = EnvAccessor()

        self._model.inference_results.data_changed.connect(self.inference_result_changed)

        self.setWindowTitle("Lock Out Detection Demo")
        

        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()

        self.main_layout = QVBoxLayout()
        self.image_label = InferenceResultImageLabel(r"./views/floor.png")
        self.image_label.setScaledContents(True)  # QLabelに合わせて画像をリサイズ
        self.image_label.setFixedWidth(screen_geometry.width())
        self.image_label.setFixedHeight(screen_geometry.height() - 50)
        self.image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.message_label = QLabel()
        self.message_label.setText("危険地域に人はいません。")
        self.message_label.setStyleSheet("font-size: 32px; color: white;")
        self.message_label.setFixedWidth(screen_geometry.width())
        self.message_label.setFixedHeight(50)
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.main_layout.addWidget(self.image_label)
        self.main_layout.addWidget(self.message_label)

        # メインウィジェットにレイアウトを設定
        self.setLayout(self.main_layout)

        # 終了イベントの処理を設定
        app.aboutToQuit.connect(self.on_exit)

        # 自動で推論を開始
        self._controller.start_inference(self.env_accessor.get_device_id())
        self.timer_proc()


    # タイマー制御
    def timer_proc(self):
        self.timer = QTimer(self)
        self.timer.setInterval(500)
        self.timer.timeout.connect(self.interval_timer)
        self.timer.start()

    def interval_timer(self):
        self._controller.get_inference_result(self.env_accessor.get_device_id())        

    def inference_result_changed(self, updated_list):
        self.draw_inference() 

    def draw_inference(self):        
        self.image_label.clear_inference_result()  

        inferences = self._model.inference_results.get_list()

        if len(inferences) == 0:
            self.message_label.setText("危険地域に人はいません。")
            self.message_label.setStyleSheet("font-size: 32px; color: white;")
        else:
            self.message_label.setText(f"危険地域からただちに離れてください。{len(inferences)}名")
            self.message_label.setStyleSheet("font-size: 32px; color: red;")

        for inference in inferences:
            self.image_label.add_inference_result(QRect(*inference))

    @Slot()
    def on_exit(self):
        print("アプリケーションが終了されました。")
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

            original_size = (320, 320)
            display_size = (self.width(), self.height())

            transformed_bbox = self.transform_bbox(rect, original_size, display_size)

            painter.drawRect(transformed_bbox)
            painter.drawText(transformed_bbox.x() + 10, transformed_bbox.y() + 20, f"{transformed_bbox.x()},{transformed_bbox.y()},{transformed_bbox.width()},{transformed_bbox.height()}")


    def transform_bbox(self, original_bbox:QRect, original_size, display_size):
        # 元の画像サイズと表示サイズを取得
        original_width, original_height = original_size
        display_width, display_height = display_size

        # 横方向と縦方向のスケールを計算
        scale_x = display_width / original_width
        scale_y = display_height / original_height

        # 元のBoundingBoxの座標をスケーリング
        transformed_bbox = QRect()
        transformed_bbox.setX(int(original_bbox.x() * scale_x))
        transformed_bbox.setY(int(original_bbox.y() * scale_y))
        transformed_bbox.setWidth(int(original_bbox.width() * scale_x))
        transformed_bbox.setHeight(int(original_bbox.height() * scale_y))

        return transformed_bbox