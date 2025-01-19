from PySide6.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QStackedWidget, QLineEdit, QGridLayout, QSizePolicy
from PySide6.QtGui import QPixmap, QPainter, QPen, QColor, QFont
from PySide6.QtCore import Slot, QTimer, Qt, QRect, Signal, QByteArray

from models.model import Model
from controllers.controller import Controller
import base64

import os
from dotenv import load_dotenv

from wifi import Cell
import platform
import multiprocessing
import subprocess
import re

class EnvAccessor():
    device_id = ""
    command_param_file_name = ""

    def __init__(self) :
        load_dotenv()
        self.device_id = os.getenv("DEVICE_ID")
        self.command_param_file_name = os.getenv("COMMAND_PARAMETER_FILE_NAME")
        auto_inference_config = os.getenv("AUTO_INFERENCE")
        if auto_inference_config == "" :
            self.auto_inference = False
        else:
            self.auto_inference = os.getenv("AUTO_INFERENCE").lower() == "true"

    def get_device_id(self):
        return self.device_id

    def set_device_id(self, value):
        self.device_id = value

    def get_command_param_file_name(self):
        return  self.command_param_file_name

    def set_command_param_file_name(self, value):
        self.command_param_file_name = value


    def save_env(self):
        with open(".env", "w", encoding="utf-8") as file:
            file.write(f"DEVICE_ID={self.device_id}\n")
            file.write(f"COMMAND_PARAMETER_FILE_NAME={self.command_param_file_name}\n")


# モニタリング画面
class MonitoringPage(QWidget):   
    def __init__(self, stacked_widget :QStackedWidget, model :Model, controller :Controller):
        super().__init__()

        self.stacked_widget = stacked_widget
        self._model = model
        self._controller = controller
        self.env_accessor = EnvAccessor()

        self._model.inference_results.data_changed.connect(self.inference_result_changed)

        main_layout = QHBoxLayout()

        # サブのレイアウト(左)
        sub_l_layout = QVBoxLayout()
        self.image_label = InferenceResultImageLabel(r"./views/base.png")
        self.image_label.setScaledContents(True)  # QLabelに合わせて画像をリサイズ
        
        self.image_label.setFixedWidth(750)
        self.image_label.setFixedHeight(750)

        sub_l_layout.addWidget(self.image_label)


        # サブのレイアウト(右)
        sub_r_layout = QVBoxLayout()

        self.menu_label = QLabel()
        self.menu_label = QLabel("AITRIOS HUB Demo Menu")
        self.menu_label.setStyleSheet("font-size: 32px; color: white;")
        self.menu_label.setFixedHeight(50)

        self.inference_start_button = QPushButton("Inference Start")
        self.inference_start_button.setFixedHeight(100)
        self.inference_start_button.setStyleSheet("font-size: 32px;")
        self.inference_start_button.clicked.connect(self.inference_start_button_clicked)


        self.inference_stop_button = QPushButton("Inference Stop")
        self.inference_stop_button.setFixedHeight(100)
        self.inference_stop_button.setStyleSheet("font-size: 32px;")
        self.inference_stop_button.clicked.connect(self.inference_stop_button_clicked)

        self.setting_geo_button = QPushButton("""Setting ROI\r\n(Region of Interest)""")
        self.setting_geo_button.setFixedHeight(100)
        self.setting_geo_button.setStyleSheet("font-size: 32px;")
        self.setting_geo_button.clicked.connect(self.setting_geo_button_clicked)

        self.setting_host_button = QPushButton("Setting LocalSV")
        self.setting_host_button.setFixedHeight(100)
        self.setting_host_button.setStyleSheet("font-size: 32px;")
        self.setting_host_button.clicked.connect(self.setting_host_button_clicked)


        self.setting_device_button = QPushButton("Setting Device")
        self.setting_device_button.setFixedHeight(100)
        self.setting_device_button.setStyleSheet("font-size: 32px;")
        self.setting_device_button.clicked.connect(self.setting_device_button_clicked)

        self.setup_camera_button = QPushButton("Setup Camera")
        self.setup_camera_button.setFixedHeight(100)
        self.setup_camera_button.setStyleSheet("font-size: 32px;")
        self.setup_camera_button.clicked.connect(self.setup_camera_button_clicked)


        sub_r_layout.addWidget(self.menu_label)
        sub_r_layout.addWidget(self.inference_start_button)
        sub_r_layout.addWidget(self.inference_stop_button)
        sub_r_layout.addWidget(self.setting_geo_button)
        sub_r_layout.addWidget(self.setting_host_button)
        sub_r_layout.addWidget(self.setting_device_button)
        sub_r_layout.addWidget(self.setup_camera_button)

        # メインレイアウトに追加
        main_layout.addLayout(sub_l_layout)
        main_layout.addSpacing(50)
        main_layout.addLayout(sub_r_layout)

        # メインウィジェットにレイアウトを設定
        self.setLayout(main_layout)
        
        self.timer_proc()

    def inference_start_button_clicked(self):
        # 推論開始
        print("inference_start_button_clicked")
        self._controller.start_inference(self.env_accessor.get_device_id())
        self.timer.start()

    def inference_stop_button_clicked(self):
        # 推論終了
        print("inference_stop_button_clicked")
        self._controller.stop_inference(self.env_accessor.get_device_id())
        self.timer.stop()

    def setting_geo_button_clicked(self):
        # 設定画面開く
        print("setting_geo_button_clicked")
        self.stacked_widget.setCurrentIndex(1)

    def setting_host_button_clicked(self):
        # 設定画面開く
        print("setting_host_button_clicked")
        self.stacked_widget.setCurrentIndex(2)

    def setting_device_button_clicked(self):
        # 設定画面開く
        print("setting_device_button_clicked")
        self.stacked_widget.setCurrentIndex(3)

    def setup_camera_button_clicked(self):
        # 設定画面開く
        print("setup_camera_button_clicked")
        self.stacked_widget.setCurrentIndex(4)


    # タイマー制御
    def timer_proc(self):
        self.timer = QTimer(self)
        self.timer.setInterval(500)
        self.timer.timeout.connect(self.interval_timer)

    def interval_timer(self):
        self._controller.get_inference_result(self.env_accessor.get_device_id())        

    def inference_result_changed(self, updated_list):
        self.draw_main_mode() 

    def draw_main_mode(self):
        self.image_label.clear_inference_result()  

        for inference in self._model.inference_results.get_list():
            self.image_label.add_inference_result(QRect(*inference))

    # ウィンドウアクティブ制御
    def active(self):
        self.timer.stop()

    def deactive(self):
        self.timer.stop()


# ジオフェンシング設定画面
class GeoSettingPage(QWidget):   
    def __init__(self, stacked_widget :QStackedWidget, model :Model, controller :Controller):
        super().__init__()
        self.stacked_widget = stacked_widget
        self._model = model
        self._controller = controller
        self.env_accessor = EnvAccessor()

        main_layout = QHBoxLayout()

        # サブのレイアウト(左)
        sub_l_layout = QVBoxLayout()

        # カメラ画像
        self.image_label = CroppableImageLabel(r"./views/base.png")
        self.set_preview_image()
        self.image_label.setScaledContents(True) 
        self.image_label.setFixedWidth(640) 
        self.image_label.setFixedHeight(480) 
        self.image_label.rectangleSelected.connect(self.on_rectangle_selected)
        sub_l_layout.addWidget(self.image_label)


        # サブのレイアウト(右)
        sub_r_layout = QVBoxLayout()

        self.danger_area_label = QLabel()
        self.danger_area_label = QLabel("警告範囲を指定してください")
        self.danger_area_label.setStyleSheet("font-size: 32px; color: white;")
        self.danger_area_label.setFixedHeight(50)

        danger_area_layout = QVBoxLayout()
        self.danger_x_text_box = QLineEdit()
        self.danger_x_text_box.setPlaceholderText("CropHOffset: 0-4055")
        self.danger_x_text_box.setStyleSheet("font-size: 32px; color: white;")
        self.danger_x_text_box.setFixedHeight(50)

        self.danger_y_text_box = QLineEdit()
        self.danger_y_text_box.setPlaceholderText("CropVOffset: 0-3039")
        self.danger_y_text_box.setStyleSheet("font-size: 32px; color: white;")
        self.danger_y_text_box.setFixedHeight(50)

        self.danger_w_text_box = QLineEdit()
        self.danger_w_text_box.setPlaceholderText("CropHSize: 0-4056")
        self.danger_w_text_box.setStyleSheet("font-size: 32px; color: white;")
        self.danger_w_text_box.setFixedHeight(50)

        self.danger_h_text_box = QLineEdit()
        self.danger_h_text_box.setPlaceholderText("CropVSize: 0-3040")
        self.danger_h_text_box.setStyleSheet("font-size: 32px; color: white;")
        self.danger_h_text_box.setFixedHeight(50)

        danger_area_layout.addWidget(self.danger_area_label)
        danger_area_layout.addWidget(self.danger_x_text_box)
        danger_area_layout.addWidget(self.danger_y_text_box)
        danger_area_layout.addWidget(self.danger_w_text_box)
        danger_area_layout.addWidget(self.danger_h_text_box)

        self.save_button = QPushButton("保　存")
        self.save_button.setFixedHeight(100)
        self.save_button.setStyleSheet("font-size: 32px;")
        self.save_button.clicked.connect(self.save_button_clicked)

        self.back_button = QPushButton("戻　る")
        self.back_button.setFixedHeight(100)
        self.back_button.setStyleSheet("font-size: 32px;")
        self.back_button.clicked.connect(self.back_button_clicked)


        sub_r_layout.addLayout(danger_area_layout)
        sub_r_layout.addWidget(self.save_button)
        sub_r_layout.addWidget(self.back_button)

        # メインレイアウトに追加
        main_layout.addLayout(sub_l_layout)
        main_layout.addSpacing(50)
        main_layout.addLayout(sub_r_layout)

        # メインウィジェットにレイアウトを設定
        self.setLayout(main_layout)

        self.timer_proc()

    # 矩形の選択が完了したときに呼ばれる処理
    def on_rectangle_selected(self, rect:QRect):
        # 画像のサイズが違うため、補正計算が必要
        # 元の矩形と画像サイズ
        original_size = (640, 480) # 将来的に変動できるようにする
        target_size = (4056, 3040) # 将来的に変動できるようにする

        # 変換後の矩形座標
        new_rect = self.scale_rectangle(rect, original_size, target_size)

        self.danger_x_text_box.setText(str(new_rect.x()))
        self.danger_y_text_box.setText(str(new_rect.y()))
        self.danger_w_text_box.setText(str(new_rect.x() + new_rect.width()))
        self.danger_h_text_box.setText(str(new_rect.y() + new_rect.height()))


    # Previewの画像とカメラの句ロッピングの画像は解像度が異なるのでスケール変換する
    # :param original_rect: 元の矩形座標 (x1, y1, x2, y2)
    # :param original_size: 元の画像サイズ (width, height)
    # :param target_size: 変換先の画像サイズ (width, height)
    def scale_rectangle(self, original_rect:QRect, original_size, target_size):
        # スケール比率の計算
        scale_x = target_size[0] / original_size[0]
        scale_y = target_size[1] / original_size[1]

        # 元の矩形の座標をスケーリング
        x = int(original_rect.x() * scale_x)
        y = int(original_rect.y() * scale_y)
        w = int(original_rect.width() * scale_x)
        h = int(original_rect.height() * scale_y)

        return QRect(x, y, w, h)

    def save_button_clicked(self):
        # 保存する
        print("save_button_clicked")
        x = int(self.danger_x_text_box.text())
        y = int(self.danger_y_text_box.text())
        width = int(self.danger_w_text_box.text())
        height = int(self.danger_h_text_box.text())
        rect = (x, y, width, height)

        self._controller.set_config_geo(self.env_accessor.get_command_param_file_name(), rect)        
        self.stacked_widget.setCurrentIndex(0)

    def back_button_clicked(self):  
        self.stacked_widget.setCurrentIndex(0)

    # タイマー制御
    def timer_proc(self):
        self.timer = QTimer(self)
        self.timer.setInterval(10000)
        self.timer.timeout.connect(self.interval_timer)

    def interval_timer(self):
        self.set_preview_image()

    def set_preview_image(self):
        try:
            preview_image = self._controller.get_preview_image(self.env_accessor.get_device_id())
            image_data = base64.b64decode(preview_image)
            byte_array = QByteArray(image_data)
            pixmap = QPixmap()
            pixmap.loadFromData(byte_array)
            self.image_label.setPixmap(pixmap)
        except:
            pass

    # ウィンドウアクティブ制御
    def active(self):
        self.timer.start()

    def deactive(self):
        self.timer.stop()

# ローカルサーバーのIPアドレス設定画面
class LocalSVSettingPage(QWidget):
    def __init__(self, stacked_widget :QStackedWidget, model :Model, controller :Controller):
        super().__init__()
        self.stacked_widget = stacked_widget
        self._model = model
        self._controller = controller
        self.env_accessor = EnvAccessor()

        main_layout = QVBoxLayout()
        item_layout = QHBoxLayout()        
        self.host_label = QLabel("ローカルサーバー")        
        self.host_label.setStyleSheet("font-size: 32px; color: white;")
        self.host_label.setFixedHeight(50)
    
        self.host_text_box = QLineEdit()
        self.host_text_box.setPlaceholderText("ここにIPアドレスとポート番号を入力してください...")
        self.host_text_box.setText("http://" + self._controller.ip_address + ":8080")
        
        self.host_text_box.setStyleSheet("font-size: 32px; color: white;")
        self.host_text_box.setFixedHeight(50)

        item_layout.addWidget(self.host_label)
        item_layout.addWidget(self.host_text_box)
        main_layout.addLayout(item_layout)

        self.save_button = QPushButton("保　存")
        self.save_button.setFixedHeight(100)
        self.save_button.setStyleSheet("font-size: 32px;")
        self.save_button.clicked.connect(self.save_button_clicked)

        self.back_button = QPushButton("戻　る")
        self.back_button.setFixedHeight(100)
        self.back_button.setStyleSheet("font-size: 32px;")
        self.back_button.clicked.connect(self.back_button_clicked)

        main_layout.addWidget(self.save_button)
        main_layout.addWidget(self.back_button)

        self.setLayout(main_layout)

    def save_button_clicked(self):
        # 保存する
        print("save_button_clicked")
        self._controller.set_config_host(self.env_accessor.get_command_param_file_name(), self.host_text_box.text())
        self.stacked_widget.setCurrentIndex(0)

    def back_button_clicked(self):  
        self.stacked_widget.setCurrentIndex(0)

    # ウィンドウアクティブ制御
    def active(self):
        pass

    def deactive(self):
        pass

# デバイス設定画面
class DeviceSettingPage(QWidget):
    def __init__(self, stacked_widget :QStackedWidget, model :Model, controller :Controller):
        super().__init__()
        self.stacked_widget = stacked_widget
        self._model = model
        self._controller = controller

        self.env_accessor = EnvAccessor()

        main_layout = QVBoxLayout()
        item_layout = QGridLayout()
        
        self.device_id_label = QLabel("デバイスID")        
        self.device_id_label.setStyleSheet("font-size: 32px; color: white;")
        self.device_id_label.setFixedHeight(50)
    
        self.device_id_text_box = QLineEdit()
        self.device_id_text_box.setPlaceholderText("ここにデバイスIDを入力してください...")
        self.device_id_text_box.setText(self.env_accessor.get_device_id())
        self.device_id_text_box.setStyleSheet("font-size: 32px; color: white;")
        self.device_id_text_box.setFixedHeight(50)

        item_layout.addWidget(self.device_id_label, 0, 0)
        item_layout.addWidget(self.device_id_text_box, 0, 1)
        item_layout.setSpacing(50)

        self.command_param_label = QLabel("コマンドパラメータ名")        
        self.command_param_label.setStyleSheet("font-size: 32px; color: white;")
        self.command_param_label.setFixedHeight(50)
    
        self.command_param_text_box = QLineEdit()
        self.command_param_text_box.setPlaceholderText("ここにコマンドパラメータ名を入力してください...")
        self.command_param_text_box.setText(self.env_accessor.get_command_param_file_name())
        self.command_param_text_box.setStyleSheet("font-size: 32px; color: white;")
        self.command_param_text_box.setFixedHeight(50)

        item_layout.addWidget(self.command_param_label)
        item_layout.addWidget(self.command_param_text_box)
        main_layout.addLayout(item_layout)

        self.save_button = QPushButton("保　存")
        self.save_button.setFixedHeight(100)
        self.save_button.setStyleSheet("font-size: 32px;")
        self.save_button.clicked.connect(self.save_button_clicked)

        self.back_button = QPushButton("戻　る")
        self.back_button.setFixedHeight(100)
        self.back_button.setStyleSheet("font-size: 32px;")
        self.back_button.clicked.connect(self.back_button_clicked)

        main_layout.addWidget(self.save_button)
        main_layout.addWidget(self.back_button)
        
        self.setLayout(main_layout)

    def save_button_clicked(self):
        # 保存する
        print("save_button_clicked")
        self.env_accessor.set_device_id(self.device_id_text_box.text())
        self.env_accessor.set_command_param_file_name(self.command_param_text_box.text())
        self.env_accessor.save_env()
        self.stacked_widget.setCurrentIndex(0)

    def back_button_clicked(self):  
        self.stacked_widget.setCurrentIndex(0)
        
    # ウィンドウアクティブ制御
    def active(self):
        pass

    def deactive(self):
        pass

# カメラ設定画面
class SetUpCameraPage(QWidget):   
    def __init__(self, stacked_widget :QStackedWidget, model :Model, controller :Controller):
        super().__init__()
        self.stacked_widget = stacked_widget
        self._model = model
        self._controller = controller

        main_layout = QHBoxLayout()

        # サブのレイアウト(左)
        sub_l_layout = QVBoxLayout()

        # QR画像を取る

        # カメラ画像
        self.image_label = QLabel(self)
        self.image_label.setScaledContents(True)  # QLabelに合わせて画像をリサイズ
        self.image_label.setFixedWidth(600)  # 画像の高さを設定
        self.image_label.setFixedHeight(600)  # 画像の高さを設定
        sub_l_layout.addWidget(self.image_label)


        # サブのレイアウト(右)
        sub_r_layout = QVBoxLayout()
        item_layout = QGridLayout()
        
        self.NTP_label = QLabel("NTPサーバー")        
        self.NTP_label.setStyleSheet("font-size: 32px; color: white;")
        self.NTP_label.setFixedHeight(50)
    
        self.NTP_value_label = QLabel("1.jp.pool.ntp.org")
        self.NTP_value_label.setStyleSheet("font-size: 32px; color: white;")
        self.NTP_value_label.setFixedHeight(50)

        item_layout.addWidget(self.NTP_label, 0, 0)
        item_layout.addWidget(self.NTP_value_label, 0, 1)
        item_layout.setSpacing(50)

        credential = self.get_current_wifi_credential()

        if credential:
            self.ssid = credential['SSID']
            self.wifi_pwd = credential['Password']
        else:
            self.ssid = ""
            self.wifi_pwd = ""

        self.SSID_label = QLabel("SSID")        
        self.SSID_label.setStyleSheet("font-size: 32px; color: white;")
        self.SSID_label.setFixedHeight(50)

        self.SSID_value_label = QLabel(self.ssid)
        self.SSID_value_label.setStyleSheet("font-size: 32px; color: white;")
        self.SSID_value_label.setFixedHeight(50)

        item_layout.addWidget(self.SSID_label, 1, 0)
        item_layout.addWidget(self.SSID_value_label, 1, 1)
        item_layout.setSpacing(50)

        self.wifi_pwd_label = QLabel("Password")        
        self.wifi_pwd_label.setStyleSheet("font-size: 32px; color: white;")
        self.wifi_pwd_label.setFixedHeight(50)

        self.wifi_pwd_value_label = QLabel(self.wifi_pwd)
        self.wifi_pwd_value_label.setStyleSheet("font-size: 32px; color: white;")
        self.wifi_pwd_value_label.setFixedHeight(50)

        item_layout.addWidget(self.wifi_pwd_label, 2, 0)
        item_layout.addWidget(self.wifi_pwd_value_label, 2, 1)
        item_layout.setSpacing(50)


        qr_image = self._controller.get_provisioning_qr_code(self.NTP_value_label.text(), self.ssid, self.wifi_pwd)
        image_data = base64.b64decode(qr_image)
        byte_array = QByteArray(image_data)
        pixmap = QPixmap()
        pixmap.loadFromData(byte_array)
        self.image_label.setPixmap(pixmap)

        self.back_button = QPushButton("戻　る")
        self.back_button.setFixedHeight(100)
        self.back_button.setStyleSheet("font-size: 32px;")
        self.back_button.clicked.connect(self.back_button_clicked)

        sub_r_layout.addLayout(item_layout)
        sub_r_layout.addWidget(self.back_button)

        # メインレイアウトに追加
        main_layout.addLayout(sub_l_layout)
        main_layout.addSpacing(50)
        main_layout.addLayout(sub_r_layout)

        # メインウィジェットにレイアウトを設定
        self.setLayout(main_layout)

    def back_button_clicked(self):  
        self.stacked_widget.setCurrentIndex(0)


    def get_current_wifi_credential(self):
        if platform.system() == "Windows":
            return self.get_current_wifi_credential_windows()
        elif platform.system() == "Linux":
            return self.get_current_wifi_credential_linux()
        else:
            print("Unsupported Operating System")
            return []

    def get_current_wifi_credential_windows(self):
        try:
            # 現在接続中のWi-FiのSSIDを取得
            result = subprocess.check_output("netsh wlan show interfaces", shell=True).decode('utf-8')
            ssid_match = re.search(r"SSID\s*:\s*(.+)", result)
            
            if not ssid_match:
                print("No Wi-Fi connection found.")
                return None

            ssid = ssid_match.group(1).strip()

            # 現在接続中のWi-Fiのパスワードを取得
            result = subprocess.check_output(f'netsh wlan show profile name="{ssid}" key=clear', shell=True).decode('utf-8')
            password_match = re.search(r"主要なコンテンツ\s*:\s*(.+)", result)
            password = password_match.group(1).strip() if password_match else "No Password"

            return {"SSID": ssid, "Password": password}
        except subprocess.CalledProcessError as e:
            print(f"Error executing Windows command: {e}")
            return None

    def get_current_wifi_credential_linux(self):
        try:
            # 現在接続中のWi-FiのSSIDを取得
            result = subprocess.check_output("iwgetid -r", shell=True).decode('utf-8').strip()
            
            if not result:
                print("No Wi-Fi connection found.")
                return None

            ssid = result

            # NetworkManagerの設定ファイルからパスワードを取得
            import os
            nm_path = "/etc/NetworkManager/system-connections"
            
            if not os.path.exists(nm_path):
                print("NetworkManager configuration directory not found.")
                return None

            for filename in os.listdir(nm_path):
                filepath = os.path.join(nm_path, filename)
                with open(filepath, 'r') as f:
                    content = f.read()
                    if f"ssid={ssid}" in content:
                        psk_match = re.search(r'psk=(.*)', content)
                        password = psk_match.group(1).strip() if psk_match else "No Password"
                        return {"SSID": ssid, "Password": password}

            return {"SSID": ssid, "Password": "No Password Found"}
        except subprocess.CalledProcessError as e:
            print(f"Error executing Linux command: {e}")
            return None
        except Exception as e:
            print(f"Error: {e}")
            return None

class AITRIOSHubDemoView(QWidget):    
    def __init__(self, model :Model, controller :Controller):
        super().__init__()
        self._model = model
        self._controller = controller

        self.setWindowTitle("AITRIOS HUB Demo App")
        self.setGeometry(0, 0, 1280, 800)

        self.setStyleSheet("""
            QWidget {
                background-color: black;
                color: white;
                font-size: 14px;
            }
            QPushButton {
                background-color: darkgray;
                border: 1px solid white;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: gray;
            }
        """)
        # QStackedWidgetの作成
        self.stacked_widget = QStackedWidget()
        
        self.monitoring_page = MonitoringPage(self.stacked_widget, self._model, self._controller)
        self.geo_setting_page = GeoSettingPage(self.stacked_widget, self._model, self._controller)        
        self.host_setting_page = LocalSVSettingPage(self.stacked_widget, self._model, self._controller)
        self.device_setting_page = DeviceSettingPage(self.stacked_widget, self._model, self._controller)
        self.setup_camera_page = SetUpCameraPage(self.stacked_widget, self._model, self._controller)
        
        self.stacked_widget.addWidget(self.monitoring_page)
        self.stacked_widget.addWidget(self.geo_setting_page)
        self.stacked_widget.addWidget(self.host_setting_page)
        self.stacked_widget.addWidget(self.device_setting_page)
        self.stacked_widget.addWidget(self.setup_camera_page)

        self.stacked_widget.currentChanged.connect(self.on_page_changed)

        # メインレイアウトにQStackedWidgetを追加
        layout = QVBoxLayout()
        layout.addWidget(self.stacked_widget)
        self.setLayout(layout)

    def on_page_changed(self, index):
        self.monitoring_page.deactive()
        self.geo_setting_page.deactive()
        self.host_setting_page.deactive()
        self.device_setting_page.deactive()
        match index:
            case 0:
                self.monitoring_page.active()
            case 1:
                self.geo_setting_page.active()
            case 2:
                self.host_setting_page.active()
            case 3:
                self.device_setting_page.active()        


# マウスによるクロップ可能なイメージラベル
class CroppableImageLabel(QLabel):
    # 矩形選択が終わったときに発行するシグナル (選択された矩形の情報を渡す)
    rectangleSelected = Signal(QRect)

    def __init__(self, image_path):
        super().__init__()
        self.pixmap = QPixmap(image_path)
        self.setPixmap(self.pixmap)
        self.setMouseTracking(True)  # マウスの追跡を有効化

        # 矩形の始点と終点
        self.start_point = None
        self.end_point = None
        self.drawing = False

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.start_point = event.pos()
            self.end_point = event.pos()
            self.drawing = True
            self.update()

    def mouseMoveEvent(self, event):
        if self.drawing:
            self.end_point = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.end_point = event.pos()
            self.drawing = False
            self.update()
            # 矩形選択が終わったときにシグナルを発行
            rect = self._calculate_rect(self.start_point, self.end_point)
            self.rectangleSelected.emit(rect)

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.start_point and self.end_point:
            painter = QPainter(self)
            pen = QPen(QColor(255, 0, 0), 2, Qt.PenStyle.SolidLine)
            painter.setPen(pen)
            painter.drawRect(self._calculate_rect(self.start_point, self.end_point))

    def _calculate_rect(self, start, end):
        # 始点と終点から矩形を作成
        x = min(start.x(), end.x())
        y = min(start.y(), end.y())
        width = abs(start.x() - end.x())
        height = abs(start.y() - end.y())
        return QRect(x, y, width, height)
    
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