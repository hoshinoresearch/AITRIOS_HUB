from PySide6.QtCore import QObject
from models.model import Model
import requests
import socket
from datetime import datetime, timezone

class Controller(QObject):
    ip_address = ""

    def __init__(self, model :Model):
        super().__init__()
        self._model = model

        # 自分のアドレスからとる    
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        self.ip_address = s.getsockname()[0]
        s.close()

    def get_base_url(self):
        # 自分のアドレスからとる        
        base_url = f"http://{self.ip_address}:8080"
        return base_url

    def get_inference_result(self, device_id:str):
        response = requests.get(f"{self.get_base_url()}/{device_id}/inference_result/")
        if response.status_code != 200:
            return
        
        json_data = response.json()
        print(json_data)
        if json_data["count"] == 0 or json_data["inferences"] == {} or json_data["inferences"][0]['P'] == -1 :
            self._model.lock_out_detection_people_cnt = 0
            inference_results = []
            self._model.inference_results.append_all(inference_results)
        else :
            date_object = datetime.fromisoformat(json_data["inferences"][0]['T']).replace(tzinfo=timezone.utc)
            now = datetime.now(timezone.utc)
            time_difference = now - date_object
            print(f"現在時刻との差:{time_difference.total_seconds()}秒")
            # 10秒未満は有効なデータとする
            if time_difference.total_seconds() <= 10:
                self._model.lock_out_detection_people_cnt = json_data["count"]
                inference_results = []
                for inference in json_data["inferences"]:
                    inference_results.append((inference['X'], inference['Y'], inference['x'], inference['y']))
                self._model.inference_results.append_all(inference_results)
            else:
                inference_results = []
                self._model.inference_results.append_all(inference_results)

    def start_inference(self, device_id:str) :
        print("推論開始")
        payload  = {
            "device_id": device_id
        }

        print(self.get_base_url())
        print(payload)
        response = requests.post(f"{self.get_base_url()}/{device_id}/start_inference/", json=payload)
        print(response)
        if response.status_code != 200:
            return
        
    def stop_inference(self, device_id:str) :
        print("推論停止")
        payload  = {
            "device_id": device_id
        }
        response = requests.post(f"{self.get_base_url()}/{device_id}/stop_inference/", json=payload)
        print(response)
        if response.status_code != 200:
            return

    def set_config_host(self, file_name:str, host_url:str) :
        print("ホストの設定")
        payload  = {
            "host_url": f"{host_url}"
        }
        
        response = requests.post(f"{self.get_base_url()}/{file_name}/set_command_param_for_local_server_address/", json=payload)
        if response.status_code != 200:
            return
        print(response)

    def set_config_geo(self, file_name:str, rect) :
        print("CROPサイズの設定")
        x, y, width, height = rect
        
        payload  = {
            "x": x,
            "y": y,
            "width": width,
            "height": height
        }
        print(payload)
        
        response = requests.post(f"{self.get_base_url()}/{file_name}/set_command_param_for_crop_size/", json=payload)
        if response.status_code != 200:
            return
        print(response)

    def get_preview_image(self, device_id:str):
        response = requests.get(f"{self.get_base_url()}/{device_id}/get_preview_image/")
        if response.status_code != 200:
            return
        
        json_data = response.json()
        return json_data["contents"]

    def get_provisioning_qr_code(self, ntp:str, wifi_ssid:str, wifi_pass:str):
        payload  = {
            "ntp": ntp,
            "wifi_ssid": wifi_ssid,
            "wifi_pass": wifi_pass
        }        
        response = requests.post(f"{self.get_base_url()}/get_provisioning_qr_code/", json=payload)
        if response.status_code != 200:
            return
        
        json_data = response.json()
        return json_data["contents"]
