import base64
import json
import requests
import cv2
import numpy as np

class Utils:
    @staticmethod
    def Base64EncodedStr(data):
        if type(data) is str:
            data = data.encode("utf-8")
        _encoded_data = base64.b64encode(data)
        _encoded_str = str(_encoded_data).replace("b'", "").replace("'", "")
        return str(_encoded_str)
    @staticmethod
    def Base64ToCV2(img_str):
    
        if "base64," in img_str:
            # DATA URI の場合、data:[<mediatype>][;base64], を除く
            _img_str = img_str.split(",")[1]
        else:
            _img_str = img_str
            
        # Base64文字列をデコードし、バイト列に変換
        _img_data = base64.b64decode(_img_str)
        
        # バイト列をNumPy配列に変換
        _nparr = np.frombuffer(_img_data, np.uint8)
        
        # NumPy配列をOpenCVの画像形式に変換
        _img = cv2.imdecode(_nparr, cv2.IMREAD_COLOR)
        image_rgb = cv2.cvtColor(_img, cv2.COLOR_BGR2RGB)
        return image_rgb


class ConsoleRESTAPI:
    def __init__(self, baseURL, client_id, client_secret, gcs_okta_domain):
        # Project information

        self.BASE_URL = baseURL
        CLIENT_ID = client_id
        CLIENT_SECRET = client_secret
        self.GCS_OKTA_DOMAIN = gcs_okta_domain
        self.AUTHORIZATION_CODE = Utils.Base64EncodedStr(CLIENT_ID + ":" + CLIENT_SECRET)
        
    ##########################################################################
    # Low Level APIs
    ##########################################################################
    def GetToken(self):
        headers = {
            "accept": "application/json",
            "authorization": "Basic " + self.AUTHORIZATION_CODE,
            "cache-control": "no-cache",
            "content-type": "application/x-www-form-urlencoded",
        }

        data = {
            "grant_type": "client_credentials",
            "scope": "system",
        }

        response = requests.post(
            url=self.GCS_OKTA_DOMAIN,
            data=data,
            headers=headers,
        )
        analysis_info = json.loads(response.text)
        token = analysis_info["access_token"]
        return token

    def GetHeaders(self, payload):
        token = self.GetToken()
        headers = {"Accept": "application/json", "Authorization": "Bearer " + token}
        if payload != {}:
            headers.setdefault("Content-Type", "application/json")
        return headers

    def Request(self, url, method, **kwargs):
        params = {}
        payload = {}
        files = {}
        url = self.BASE_URL + url

        # set parameters
        for key, val in kwargs.items():
            if val != None:
                if key == "payload":
                    # payload
                    payload = json.dumps(val)
                elif key == "files":
                    # multipart/form-data
                    files = val
                else:
                    # check parameters
                    if "{" + key + "}" in url:
                        # path parameter
                        url = url.replace("{" + key + "}", val)
                    else:
                        # query parameter
                        params.setdefault(key, str(val))

        # create header
        headers = self.GetHeaders(payload=payload)
        # call request
        try:
            response = requests.request(
                method=method, url=url, headers=headers, params=params, data=payload, files=files
            )
            analysis_info = json.loads(response.text)
        except Exception as e:
            return response.text
        return analysis_info
    
    # 推論開始
    def StartUploadInferenceResult(self, device_id):
        ret = self.Request(
            url="/devices/{device_id}/inferenceresults/collectstart",
            method="POST",
            device_id=device_id,
        )
        return ret

    # 推論終了
    def StoploadInferenceResult(self, device_id):
        ret = self.Request(
            url="/devices/{device_id}/inferenceresults/collectstop",
            method="POST",
            device_id=device_id,
        )
        return ret
    
    # プレビューイメージ取得
    def GetPreviewImage(self, device_id):
        ret = self.Request(
            url="/devices/{device_id}/images/latest",
            method="GET",
            device_id=device_id,
        )
        return ret


    # Command Parameterの全てを取得
    def GetCommandParameterFiles(self):
        ret = self.Request(
            url="/command_parameter_files",
            method="GET",
        )
        return ret

    # 特定のCommand Parameterを取得。ただしデータはエンコードされているので、結果を得るには、返却されたデータからのデコードが必要
    def ExportCommandParameterFiles(self, file_name):
        ret = self.Request(
            url="/command_parameter_files/{file_name}/export",
            method="GET",
            file_name=file_name,
        )
        return ret

    # 特定のCommand Parameterを更新。parameterはb64エンコードされたjsonを渡すこと
    def UpdateCommandParameterFiles(self, file_name, parameter):
        ret = self.Request(
            url=f"/command_parameter_files/{file_name}",
            method="PATCH",
            file_name=file_name,
            payload={
                "parameter":parameter,
                "comment":"automation"
            }
        )

        return ret
    
    # カメラのプロビジョニング用QRコード取得
    def GetProvisioningQRCode(self, ntp, wifi_ssid, wifi_pass):
        ret = self.Request(
            url="/provisioning/qrcode",
            method="GET",
            ntp=ntp,
            wifi_ssid=wifi_ssid,
            wifi_pass=wifi_pass
        )
        return ret

    
# 画像ファイルに保存する関数
def save_base64_as_image(base64_string, output_path):
    # 改行や空白を除去する
    clean_base64_string = base64_string.replace("\n", "").replace("\r", "")
    
    # Base64デコードしてバイナリデータに変換
    image_data = base64.b64decode(clean_base64_string)
    
    # 画像ファイルとして保存
    with open(output_path, "wb") as image_file:
        image_file.write(image_data)
    print(f"Image saved to {output_path}")


def main():
    base_url = "https://console.aitrios.sony-semicon.com/api/v1"
    client_id = "0oaktgw65lfAmKtBC697"
    client_secret = "41gjJ4jQDThuTAZyqZHAMlFpEkrd2oAYI259-0ru3K9jSxsWUr0aHq05QCpHjKeS"
    gcs_okta_domain = "https://auth.aitrios.sony-semicon.com/oauth2/default/v1/token"

    device_id = "Aid-80070001-0000-2000-9002-000000000a89"
    console_api = ConsoleRESTAPI(base_url, client_id, client_secret, gcs_okta_domain)
    
    response = console_api.GetPreviewImage(device_id)

    cv_img = Utils.Base64ToCV2(response["contents"])    

    # 元の画像サイズ
    original_width = 4056
    original_height = 3040

    # 画像を元の解像度にリサイズ
    resized_image = cv2.resize(cv_img, (original_width, original_height))

    # 切り抜きパラメータ指定
    CropHOffset = 100
    CropVOffset = 200
    CropHSize = 1200
    CropVSize = 1400

    # クロップ処理
    cropped_image = resized_image[CropVOffset:CropVOffset + CropVSize, CropHOffset:CropHOffset + CropHSize]

    output_image_path = 'output_image_org.jpg'
    cv2.imwrite(output_image_path, resized_image)

    output_image_path = 'output_image.jpg'
    cv2.imwrite(output_image_path, cropped_image)

    output_path = "output_image2.jpg"
    save_base64_as_image(response["contents"], output_path)
# メイン関数を呼び出す条件
if __name__ == "__main__":
    main()



