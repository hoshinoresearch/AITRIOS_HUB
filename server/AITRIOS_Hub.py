from fastapi import FastAPI, Request, status
import traceback
import logging
from Desilialize import DeserializeUtil
import json
from AITRIOSLocalDBHandler import InferenceResultTableHandler
from ConsoleWrapperLimited import ConsoleRESTAPI, Utils
from datetime import datetime, timezone
import os
from dotenv import load_dotenv


app_ins = FastAPI()
# Log format
log_format = '%(asctime)s - %(message)s'
# Set log level to INFO
logging.basicConfig(format=log_format, level=logging.INFO)


# 最後の推論結果取得
@app_ins.get("/{device_id}/inference_result")
async def get_inference_result(device_id: str, request: Request):
    logging.info("get_inference_result device_id: %s", device_id)

    # SQLiteから取り出す
    table_handler = InferenceResultTableHandler()
    record = table_handler.fetch_latestdate_by_device_id(device_id)

    json_data = table_handler.convert_to_json_multiple(record)
    table_handler.close()
    print(json_data)
    
    # TODO:最新日付のチェックをし、古い場合、または推論結果が存在しなかった場合は0件を返す
    return json_data

#------------------ AITRIOS Console Wrapper API --------------------------
load_dotenv()
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")    
base_url = "https://console.aitrios.sony-semicon.com/api/v1"
gcs_okta_domain = "https://auth.aitrios.sony-semicon.com/oauth2/default/v1/token"

@app_ins.post("/{device_id}/start_inference")
def start_inference(device_id: str, request: Request) :
    logging.info("start_inference device_id: %s", device_id)
    console_api = ConsoleRESTAPI(base_url, client_id, client_secret, gcs_okta_domain)        
    print("推論開始:}")
    response = console_api.StartUploadInferenceResult(device_id)
    print(response)
    return response

@app_ins.post("/{device_id}/stop_inference")
def stop_inference(device_id: str, request: Request) :
    logging.info("stop_inference device_id: %s", device_id)
    console_api = ConsoleRESTAPI(base_url, client_id, client_secret, gcs_okta_domain)        
    print("推論停止")
    response = console_api.StoploadInferenceResult(device_id)
    print(response)
    return response

# ローカルサーバーを設定する
@app_ins.post("/{file_name}/set_command_param_for_local_server_address")
async def set_command_param_for_local_server_address(file_name: str, request: Request):
    logging.info("set_command_param_for_local_server_address file_name: %s", file_name)
    return await update_command_parameters(file_name, request, set_local_server_address)

# CROPサイズを設定する
@app_ins.post("/{file_name}/set_command_param_for_crop_size")
async def set_command_param_for_crop_size(file_name: str, request: Request):
    logging.info("set_command_param_for_crop_size file_name: %s", file_name)
    return await update_command_parameters(file_name, request, set_crop_size)

# CommandParameter共通処理
async def update_command_parameters(file_name: str, request: Request, update_function):
    console_api = ConsoleRESTAPI(base_url, client_id, client_secret, gcs_okta_domain)        

    # コマンドパラメータを取得
    command_params = console_api.GetCommandParameterFiles()

    # 指定された file_name を持つ要素を抽出し commands 形式に整形
    command_param_data = []
    for parameter_item in command_params["parameter_list"]:
        if parameter_item["file_name"] == file_name:
            command_param_data.append({
                "commands": parameter_item["parameter"]["commands"]
            })

    if not command_param_data:
        return {"error": "File not found"}

    # 更新処理を共通関数で実行
    content = await request.body()
    json_data = json.loads(content)

    update_function(command_param_data[0]["commands"], json_data)

    # 更新後のデータをエンコードして送信
    command_param_json = json.dumps(command_param_data[0], indent=4)
    _encoded_command_param_data = Utils.Base64EncodedStr(command_param_json)

    print(command_param_json)
    print("Command Parameter更新")
    response = console_api.UpdateCommandParameterFiles(file_name, _encoded_command_param_data)
    print(response)
    return response

# ローカルサーバーを設定する
def set_local_server_address(commands, json_data):
    print(json_data)
    host_url = json_data["host_url"]

    for command in commands:
        if command["command_name"] == "StartUploadInferenceData":
            command["parameters"]["StorageName"] = host_url
            command["parameters"]["StorageNameIR"] = host_url


# CROPサイズを設定する
def set_crop_size(commands, json_data):
    print(json_data)
    new_crop_x_size = json_data["x"]
    new_crop_y_size = json_data["y"]
    new_crop_w_size = json_data["width"]
    new_crop_h_size = json_data["height"]

    for command in commands:
        if command["command_name"] == "StartUploadInferenceData":
            command["parameters"]["CropHOffset"] = new_crop_x_size
            command["parameters"]["CropVOffset"] = new_crop_y_size
            command["parameters"]["CropHSize"] = new_crop_w_size
            command["parameters"]["CropVSize"] = new_crop_h_size



@app_ins.get("/{device_id}/get_preview_image")
async def get_preview_image(device_id: str, request: Request):
    logging.info("get_preview_image device_id: %s", device_id)

    console_api = ConsoleRESTAPI(base_url, client_id, client_secret, gcs_okta_domain) 
    response = console_api.GetPreviewImage(device_id)

    return response

@app_ins.post("/get_provisioning_qr_code")
async def get_provisioning_qr_code(request: Request):
    logging.info("get_provisioning_qr_code")

    content = await request.body()
    json_data = json.loads(content)
    ntp = json_data["ntp"]
    wifi_ssid = json_data["wifi_ssid"]
    wifi_pass = json_data["wifi_pass"]

    console_api = ConsoleRESTAPI(base_url, client_id, client_secret, gcs_okta_domain) 
    response = console_api.GetProvisioningQRCode(ntp, wifi_ssid, wifi_pass)

    return response


# AITRIOS ローカルHTTP用 画像受信(mode 0 or 1)
@app_ins.put("/image/{filename}")
async def update_image(filename, request: Request):
        try:
                SAVE_PATH_IMG = './image'

                logging.info("update image")
                content = await request.body()
                os.makedirs(SAVE_PATH_IMG, exist_ok=True)
                save_file(SAVE_PATH_IMG, content, filename)
                logging.info("Image File Saved: %s", filename)
                return {"status":status.HTTP_200_OK}
        except (Exception):
                traceback.print_exc()

def save_file(file_type, content, filename):
        file_path = os.path.join(file_type, filename)
        with open(file_path, 'wb') as w_fp:
                w_fp.write(content)

# AITRIOS ローカルHTTP用 推論結果受信(mode 1 or 2)
@app_ins.put("/meta/{filename}")
async def update_inference_result(filename, request: Request):
    try:
        content = await request.body()
        contentj = json.loads(content)
        inferences = contentj["Inferences"]
        inferenceresult = inferences[0]["O"]

        deserializeutil = DeserializeUtil()
        deserialize_data = deserializeutil.get_deserialize_data(inferenceresult)
        logging.info("Deserialized Data: %s", deserialize_data)
        
        # SQLiteに格納する
        table_handler = InferenceResultTableHandler()

        inserted_count = 0
        for rec, record in deserialize_data.items():
            # TODO:必要に応じ条件を変える。Class 0または1でかつ0.5以上のスコアのみ
            if (record['C'] == 0 or record['C'] == 1) and record['P'] >= 0.5:
                data = {
                    "device_id": contentj["DeviceID"],
                    "C": record['C'],
                    "T": inferences[0]["T"],
                    "P": record['P'],
                    "X": record['X'],
                    "Y": record['Y'],
                    "x": record['x'],
                    "y": record['y']
                }           
                print("Insert Data: %s", data)
                table_handler.insert_data(data)
                inserted_count = inserted_count + 1

        if inserted_count == 0:
            # 推論結果が無しのレコードを入れる
            now = datetime.now(timezone.utc)
            data = {
                "device_id": contentj["DeviceID"],
                "C": "",
                "T": now.strftime("%Y%m%d%H%M%S") + f"{now.microsecond // 1000:03d}",
                "P": -1,
                "X": -1,
                "Y": -1,
                "x": -1,
                "y": -1
            }           
            print("No Insert Data: %s", data)
            table_handler.insert_data(data)       

        table_handler.close()

        return {"status":status.HTTP_200_OK}
    except (Exception):
        traceback.print_exc()