import requests
import json


class http():
    request_id = 0

    def __init__(self, host, psk):
        self.host = host
        self.psk = psk

    def request(self, endpoint, method, params, version="1.0"):
        print("foo!")
        self.request_id += 1

        url = "http://{0}/sony/{1}".format(self.host, endpoint)
        headers = {
            "X-Auth-PSK": self.psk,
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
            "Content-Type": "application/json; charset=UTF-8"
        }

        request_params = []
        for param_name in params:
            request_params.append({param_name: params[param_name]})

        payload = {
            "method": method,
            "params": request_params,
            "version": version,
            "id": self.request_id
        }

        result = requests.post(url, headers=headers, data=json.dumps(payload))
