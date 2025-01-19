import base64
import requests
import json

class Utils:
    @staticmethod
    def Base64Decoder(data):
        if type(data) is str:
            data = data.encode("utf-8")
        _decoded_data = base64.decodebytes(data)
        return _decoded_data
    @staticmethod
    def Base64EncodedStr(data):
        if type(data) is str:
            data = data.encode("utf-8")
        _encoded_data = base64.b64encode(data)
        _encoded_str = str(_encoded_data).replace("b'", "").replace("'", "")
        return str(_encoded_str)    

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

    def GetDevices(
        self, connectionState=None, device_name=None, device_id=None, device_group_id=None
    ):
        ret = self.Request(
            url="/devices",
            method="GET",
            connectionState=connectionState,
            device_name=device_name,
            device_id=device_id,
            device_group_id=device_group_id,
        )
        return ret

    def GetImageDirectories(self, device_id=None, order_by=None):
        ret = self.Request(url="/devices/images/directories", method="GET", device_id=device_id, order_by=order_by)
        return ret
    
    def GetImages(
        self, device_id, sub_directory_name, order_by=None, number_of_images=None, skip=None
    ):
        ret = self.Request(
            url="/devices/{device_id}/images/directories/{sub_directory_name}",
            method="GET",
            device_id=device_id,
            sub_directory_name=sub_directory_name,
            order_by=order_by,
            number_of_images=number_of_images,
            skip=skip,
        )
        return ret

    def GetInferenceResults(
        self, device_id, NumberOfInferenceresults=None, filter=None, raw=None, time=None
    ):
        ret = self.Request(
            url="/devices/{device_id}/inferenceresults",
            method="GET",
            device_id=device_id,
            NumberOfInferenceresults=NumberOfInferenceresults,
            filter=filter,
            raw=raw,
            time=time,
        )
        return ret
    
    def StartUploadInferenceResult(
        self, device_id
    ):
        ret = self.Request(
            url="/devices/{device_id}/inferenceresults/collectstart",
            method="POST",
            device_id=device_id,
        )
        return ret

    def StoploadInferenceResult(
        self, device_id
    ):
        ret = self.Request(
            url="/devices/{device_id}/inferenceresults/collectstop",
            method="POST",
            device_id=device_id,
        )
        return ret

