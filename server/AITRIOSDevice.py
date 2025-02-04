import json
from dataclasses import dataclass
from typing import List

# ------------- JSONの各階層に対応するクラス定義 ------------- #

@dataclass
class DeviceProperty:
    device_name: str
    internal_device_id: str

@dataclass
class DeviceModel:
    model_version_id: str

@dataclass
class OTAConfiguration:
    UpdateModule: str
    ReplaceNetworkID: str
    PackageUri: str
    DesiredVersion: str
    HashValue: str

@dataclass
class DeviceConfiguration:
    OTA: OTAConfiguration

@dataclass
class Hardware:
    Sensor: str
    SensorId: str
    KG: str
    ApplicationProcessor: str
    LedOn: bool

@dataclass
class Version:
    SensorFwVersion: str
    SensorLoaderVersion: str
    DnnModelVersion: List[str]
    ApFwVersion: str
    ApLoaderVersion: str

@dataclass
class Status:
    Sensor: str
    ApplicationProcessor: str
    SensorTemperature: int
    HoursMeter: int

@dataclass
class OTAState:
    SensorFwLastUpdatedDate: str
    SensorLoaderLastUpdatedDate: str
    DnnModelLastUpdatedDate: List[str]
    ApFwLastUpdatedDate: str
    UpdateProgress: int
    UpdateStatus: str

@dataclass
class Image:
    FrameRate: int
    DriveMode: int

@dataclass
class Exposure:
    ExposureMode: str
    ExposureMaxExposureTime: int
    ExposureMinExposureTime: int
    ExposureMaxGain: int
    AESpeed: int
    ExposureCompensation: int
    ExposureTime: int
    ExposureGain: int
    FlickerReduction: int

# ※ JSON上のキー "LSC-ISP" や "LSC-Raw" は、Python上では「LSC_ISP」「LSC_Raw」として扱います
@dataclass
class Adjustment:
    ColorMatrix: str
    Gamma: str
    LSC_ISP: str
    LSC_Raw: str
    PreWB: str
    Dewarp: str

@dataclass
class Direction:
    Vertical: str
    Horizontal: str

@dataclass
class Network:
    ProxyURL: str
    ProxyPort: int
    ProxyUserName: str
    IPAddress: str
    SubnetMask: str
    Gateway: str
    DNS: str
    NTP: str

@dataclass
class Permission:
    FactoryReset: bool

@dataclass
class Battery:
    Voltage: int
    InUse: str
    Alarm: bool

@dataclass
class PrimaryInterval:
    ConfigInterval: int
    CaptureInterval: int
    BaseTime: str
    UploadCount: int

@dataclass
class SecondaryInterval:
    ConfigInterval: int
    CaptureInterval: int
    BaseTime: str
    UploadCount: int

@dataclass
class UploadInferenceParameter:
    UploadMethodIR: str
    StorageNameIR: str
    StorageSubDirectoryPathIR: str
    PPLParameter: str
    CropHOffset: int
    CropVOffset: int
    CropHSize: int
    CropVSize: int
    NetworkId: str

@dataclass
class PeriodicParameter:
    NetworkParameter: str
    PrimaryInterval: PrimaryInterval
    SecondaryInterval: SecondaryInterval
    UploadInferenceParameter: UploadInferenceParameter

@dataclass
class FWOperation:
    OperatingMode: str
    ErrorHandling: str
    PeriodicParameter: PeriodicParameter

@dataclass
class DeviceState:
    Hardware: Hardware
    Version: Version
    Status: Status
    OTA: OTAState
    Image: Image
    Exposure: Exposure
    Adjustment: Adjustment
    Direction: Direction
    Network: Network
    Permission: Permission
    Battery: Battery
    FWOperation: FWOperation

@dataclass
class DeviceGroup:
    device_group_id: str
    device_type: str
    comment: str
    ins_id: str
    ins_date: str
    upd_id: str
    upd_date: str

@dataclass
class Device:
    device_id: str
    place: str
    comment: str
    property: DeviceProperty
    device_type: str
    display_device_type: str
    ins_id: str
    ins_date: str
    upd_id: str
    upd_date: str
    connectionState: str
    lastActivityTime: str
    models: List[DeviceModel]
    configuration: DeviceConfiguration
    state: DeviceState
    device_groups: List[DeviceGroup]

# ------------- JSON文字列から Device クラスのインスタンスを作成する関数 ------------- #

def parse_device(json_str: str) -> Device:
    data = json.loads(json_str)

    # property 部分
    property_data = data.get("property", {})
    device_property = DeviceProperty(
        device_name=property_data.get("device_name", ""),
        internal_device_id=property_data.get("internal_device_id", "")
    )

    # models 部分
    models_data = data.get("models", [])
    models = [DeviceModel(model_version_id=item.get("model_version_id", "")) for item in models_data]

    # configuration -> OTA 部分
    config_data = data.get("configuration", {})
    ota_config = config_data.get("OTA", {})
    configuration = DeviceConfiguration(
        OTA = OTAConfiguration(
            UpdateModule = ota_config.get("UpdateModule", ""),
            ReplaceNetworkID = ota_config.get("ReplaceNetworkID", ""),
            PackageUri = ota_config.get("PackageUri", ""),
            DesiredVersion = ota_config.get("DesiredVersion", ""),
            HashValue = ota_config.get("HashValue", "")
        )
    )

    # state 全体
    state_data = data.get("state", {})

    # Hardware
    hardware_data = state_data.get("Hardware", {})
    hardware = Hardware(
        Sensor=hardware_data.get("Sensor", ""),
        SensorId=hardware_data.get("SensorId", ""),
        KG=hardware_data.get("KG", ""),
        ApplicationProcessor=hardware_data.get("ApplicationProcessor", ""),
        LedOn=hardware_data.get("LedOn", False)
    )

    # Version
    version_data = state_data.get("Version", {})
    version = Version(
        SensorFwVersion=version_data.get("SensorFwVersion", ""),
        SensorLoaderVersion=version_data.get("SensorLoaderVersion", ""),
        DnnModelVersion=version_data.get("DnnModelVersion", []),
        ApFwVersion=version_data.get("ApFwVersion", ""),
        ApLoaderVersion=version_data.get("ApLoaderVersion", "")
    )

    # Status
    status_data = state_data.get("Status", {})
    status = Status(
        Sensor=status_data.get("Sensor", ""),
        ApplicationProcessor=status_data.get("ApplicationProcessor", ""),
        SensorTemperature=status_data.get("SensorTemperature", 0),
        HoursMeter=status_data.get("HoursMeter", 0)
    )

    # OTA (state内)
    ota_state_data = state_data.get("OTA", {})
    ota_state = OTAState(
        SensorFwLastUpdatedDate=ota_state_data.get("SensorFwLastUpdatedDate", ""),
        SensorLoaderLastUpdatedDate=ota_state_data.get("SensorLoaderLastUpdatedDate", ""),
        DnnModelLastUpdatedDate=ota_state_data.get("DnnModelLastUpdatedDate", []),
        ApFwLastUpdatedDate=ota_state_data.get("ApFwLastUpdatedDate", ""),
        UpdateProgress=ota_state_data.get("UpdateProgress", 0),
        UpdateStatus=ota_state_data.get("UpdateStatus", "")
    )

    # Image
    image_data = state_data.get("Image", {})
    image = Image(
        FrameRate=image_data.get("FrameRate", 0),
        DriveMode=image_data.get("DriveMode", 0)
    )

    # Exposure
    exposure_data = state_data.get("Exposure", {})
    exposure = Exposure(
        ExposureMode=exposure_data.get("ExposureMode", ""),
        ExposureMaxExposureTime=exposure_data.get("ExposureMaxExposureTime", 0),
        ExposureMinExposureTime=exposure_data.get("ExposureMinExposureTime", 0),
        ExposureMaxGain=exposure_data.get("ExposureMaxGain", 0),
        AESpeed=exposure_data.get("AESpeed", 0),
        ExposureCompensation=exposure_data.get("ExposureCompensation", 0),
        ExposureTime=exposure_data.get("ExposureTime", 0),
        ExposureGain=exposure_data.get("ExposureGain", 0),
        FlickerReduction=exposure_data.get("FlickerReduction", 0)
    )

    # Adjustment
    adjustment_data = state_data.get("Adjustment", {})
    adjustment = Adjustment(
        ColorMatrix=adjustment_data.get("ColorMatrix", ""),
        Gamma=adjustment_data.get("Gamma", ""),
        LSC_ISP=adjustment_data.get("LSC-ISP", ""),
        LSC_Raw=adjustment_data.get("LSC-Raw", ""),
        PreWB=adjustment_data.get("PreWB", ""),
        Dewarp=adjustment_data.get("Dewarp", "")
    )

    # Direction
    direction_data = state_data.get("Direction", {})
    direction = Direction(
        Vertical=direction_data.get("Vertical", ""),
        Horizontal=direction_data.get("Horizontal", "")
    )

    # Network
    network_data = state_data.get("Network", {})
    network = Network(
        ProxyURL=network_data.get("ProxyURL", ""),
        ProxyPort=network_data.get("ProxyPort", 0),
        ProxyUserName=network_data.get("ProxyUserName", ""),
        IPAddress=network_data.get("IPAddress", ""),
        SubnetMask=network_data.get("SubnetMask", ""),
        Gateway=network_data.get("Gateway", ""),
        DNS=network_data.get("DNS", ""),
        NTP=network_data.get("NTP", "")
    )

    # Permission
    permission_data = state_data.get("Permission", {})
    permission = Permission(
        FactoryReset=permission_data.get("FactoryReset", False)
    )

    # Battery
    battery_data = state_data.get("Battery", {})
    battery = Battery(
        Voltage=battery_data.get("Voltage", 0),
        InUse=battery_data.get("InUse", ""),
        Alarm=battery_data.get("Alarm", False)
    )

    # FWOperation
    fw_operation_data = state_data.get("FWOperation", {})
    periodic_parameter_data = fw_operation_data.get("PeriodicParameter", {})
    primary_interval_data = periodic_parameter_data.get("PrimaryInterval", {})
    secondary_interval_data = periodic_parameter_data.get("SecondaryInterval", {})
    upload_inference_data = periodic_parameter_data.get("UploadInferenceParameter", {})

    fw_operation = FWOperation(
        OperatingMode=fw_operation_data.get("OperatingMode", ""),
        ErrorHandling=fw_operation_data.get("ErrorHandling", ""),
        PeriodicParameter=PeriodicParameter(
            NetworkParameter=periodic_parameter_data.get("NetworkParameter", ""),
            PrimaryInterval=PrimaryInterval(
                ConfigInterval=primary_interval_data.get("ConfigInterval", 0),
                CaptureInterval=primary_interval_data.get("CaptureInterval", 0),
                BaseTime=primary_interval_data.get("BaseTime", ""),
                UploadCount=primary_interval_data.get("UploadCount", 0)
            ),
            SecondaryInterval=SecondaryInterval(
                ConfigInterval=secondary_interval_data.get("ConfigInterval", 0),
                CaptureInterval=secondary_interval_data.get("CaptureInterval", 0),
                BaseTime=secondary_interval_data.get("BaseTime", ""),
                UploadCount=secondary_interval_data.get("UploadCount", 0)
            ),
            UploadInferenceParameter=UploadInferenceParameter(
                UploadMethodIR=upload_inference_data.get("UploadMethodIR", ""),
                StorageNameIR=upload_inference_data.get("StorageNameIR", ""),
                StorageSubDirectoryPathIR=upload_inference_data.get("StorageSubDirectoryPathIR", ""),
                PPLParameter=upload_inference_data.get("PPLParameter", ""),
                CropHOffset=upload_inference_data.get("CropHOffset", 0),
                CropVOffset=upload_inference_data.get("CropVOffset", 0),
                CropHSize=upload_inference_data.get("CropHSize", 0),
                CropVSize=upload_inference_data.get("CropVSize", 0),
                NetworkId=upload_inference_data.get("NetworkId", "")
            )
        )
    )

    device_state = DeviceState(
        Hardware=hardware,
        Version=version,
        Status=status,
        OTA=ota_state,
        Image=image,
        Exposure=exposure,
        Adjustment=adjustment,
        Direction=direction,
        Network=network,
        Permission=permission,
        Battery=battery,
        FWOperation=fw_operation
    )

    # device_groups 部分
    groups_data = data.get("device_groups", [])
    device_groups = [DeviceGroup(
        device_group_id=item.get("device_group_id", ""),
        device_type=item.get("device_type", ""),
        comment=item.get("comment", ""),
        ins_id=item.get("ins_id", ""),
        ins_date=item.get("ins_date", ""),
        upd_id=item.get("upd_id", ""),
        upd_date=item.get("upd_date", "")
    ) for item in groups_data]

    device = Device(
        device_id = data.get("device_id", ""),
        place = data.get("place", ""),
        comment = data.get("comment", ""),
        property = device_property,
        device_type = data.get("device_type", ""),
        display_device_type = data.get("display_device_type", ""),
        ins_id = data.get("ins_id", ""),
        ins_date = data.get("ins_date", ""),
        upd_id = data.get("upd_id", ""),
        upd_date = data.get("upd_date", ""),
        connectionState = data.get("connectionState", ""),
        lastActivityTime = data.get("lastActivityTime", ""),
        models = models,
        configuration = configuration,
        state = device_state,
        device_groups = device_groups
    )

    return device


def parse_devices(json_data) -> List[Device]:
    return [parse_device(json.dumps(item)) for item in json_data]

# ------------- 使用例（単一データの場合） ------------- #
if __name__ == "__main__":
    json_data = r'''
    {
        "device_id": "Aid-80070001-0000-2000-9002-000000000a89",
        "place": "",
        "comment": "",
        "property": {
            "device_name": "SHIBUYA-1st-10105-reTerminal",
            "internal_device_id": "297da0e0-7fb2-11ef-8b3e-1b5d692cccd6"
        },
        "device_type": "03",
        "display_device_type": "AIH-IVRW2",
        "ins_id": "00ufjgj8qlnnXYTe4697",
        "ins_date": "2024-10-01T05:01:05.191910+00:00",
        "upd_id": "00ufjgj8qlnnXYTe4697",
        "upd_date": "2024-12-18T01:58:11.839987+00:00",
        "connectionState": "Disconnected",
        "lastActivityTime": "2025-01-23T11:34:06+00:00",
        "models": [
            { "model_version_id": "SSDLite-MobileDet2:v2.00" },
            { "model_version_id": "_PRESET_mobiledet:v1.00" },
            { "model_version_id": "PPE_V1:v1.00" }
        ],
        "configuration": {
            "OTA": {
                "UpdateModule": "",
                "ReplaceNetworkID": "",
                "PackageUri": "",
                "DesiredVersion": "",
                "HashValue": ""
            }
        },
        "state": {
            "Hardware": {
                "Sensor": "IMX500",
                "SensorId": "101A50500A2306011964013000000000",
                "KG": "1",
                "ApplicationProcessor": "",
                "LedOn": true
            },
            "Version": {
                "SensorFwVersion": "010707",
                "SensorLoaderVersion": "020301",
                "DnnModelVersion": [
                    "0311030179440200",
                    "0311030121700100",
                    "0311030210870100"
                ],
                "ApFwVersion": "0400FAWS",
                "ApLoaderVersion": "010300"
            },
            "Status": {
                "Sensor": "Standby",
                "ApplicationProcessor": "Idle",
                "SensorTemperature": 46,
                "HoursMeter": 43
            },
            "OTA": {
                "SensorFwLastUpdatedDate": "",
                "SensorLoaderLastUpdatedDate": "",
                "DnnModelLastUpdatedDate": [
                    "20241031045419",
                    "20241214173645",
                    "20241217163153"
                ],
                "ApFwLastUpdatedDate": "20241031051753",
                "UpdateProgress": 100,
                "UpdateStatus": "Done"
            },
            "Image": {
                "FrameRate": 2997,
                "DriveMode": 1
            },
            "Exposure": {
                "ExposureMode": "auto",
                "ExposureMaxExposureTime": 20,
                "ExposureMinExposureTime": 33,
                "ExposureMaxGain": 24,
                "AESpeed": 3,
                "ExposureCompensation": 6,
                "ExposureTime": 18,
                "ExposureGain": 1,
                "FlickerReduction": 7
            },
            "Adjustment": {
                "ColorMatrix": "std",
                "Gamma": "std",
                "LSC-ISP": "std",
                "LSC-Raw": "std",
                "PreWB": "std",
                "Dewarp": "off"
            },
            "Direction": {
                "Vertical": "Normal",
                "Horizontal": "Normal"
            },
            "Network": {
                "ProxyURL": "",
                "ProxyPort": 0,
                "ProxyUserName": "",
                "IPAddress": "",
                "SubnetMask": "",
                "Gateway": "",
                "DNS": "",
                "NTP": "1.jp.pool.ntp.org"
            },
            "Permission": {
                "FactoryReset": false
            },
            "Battery": {
                "Voltage": 0,
                "InUse": "USB",
                "Alarm": false
            },
            "FWOperation": {
                "OperatingMode": "Manual",
                "ErrorHandling": "",
                "PeriodicParameter": {
                    "NetworkParameter": "",
                    "PrimaryInterval": {
                        "ConfigInterval": 0,
                        "CaptureInterval": 0,
                        "BaseTime": "00:00",
                        "UploadCount": 0
                    },
                    "SecondaryInterval": {
                        "ConfigInterval": 0,
                        "CaptureInterval": 0,
                        "BaseTime": "00:00",
                        "UploadCount": 0
                    },
                    "UploadInferenceParameter": {
                        "UploadMethodIR": "",
                        "StorageNameIR": "",
                        "StorageSubDirectoryPathIR": "",
                        "PPLParameter": "",
                        "CropHOffset": 0,
                        "CropVOffset": 0,
                        "CropHSize": 0,
                        "CropVSize": 0,
                        "NetworkId": ""
                    }
                }
            }
        },
        "device_groups": [
            {
                "device_group_id": "Anna_Kuma-Kitayo_Base",
                "device_type": "03",
                "comment": "",
                "ins_id": "00ufjgj8qlnnXYTe4697",
                "ins_date": "2024-11-17T09:33:22.261939+00:00",
                "upd_id": "00ufjgj8qlnnXYTe4697",
                "upd_date": "2024-11-17T09:33:22.261944+00:00"
            }
        ]
    }
    '''
    device_instance = parse_device(json_data)
    print(device_instance)
    print(device_instance.device_id)
    print(device_instance.models[0].model_version_id)



