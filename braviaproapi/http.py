import requests
import json


class http_exception(Exception):
    def __init__(self, message, error_code=None):
        self.error_code = error_code
        pass


class http(object):
    request_id = 0

    def __init__(self, host, psk):
        self.host = host
        self.psk = psk

    def request(self, endpoint, method, params=None, version="1.0"):
        self.request_id += 1

        url = "http://{0}/sony/{1}".format(self.host, endpoint)
        headers = {
            "X-Auth-PSK": self.psk,
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
            "Content-Type": "application/json; charset=UTF-8"
        }

        request_params = []
        if params is not None:
            for param_name in params:
                request_params.append({param_name: params[param_name]})

        payload = {
            "method": method,
            "params": request_params,
            "version": version,
            "id": self.request_id
        }

        try:
            result = requests.post(url, headers=headers, data=json.dumps(payload), timeout=5)
        except requests.exceptions.Timeout:
            raise http_exception("The request timed out. Is the device powered with the IP control interface enabled?")
        except requests.exceptions.ConnectionError as err:
            raise http_exception("A connection error occurred: {0}".format(str(err)))
        except requests.exceptions.RequestsException as err:
            raise http_exception("An unexpected error occurred while sending the request: {0}".format(str(err)))

        if result.status_code != 200:
            raise http_exception("Unexpected status code {0} received".format(str(result.status_code)))

        try:
            response = result.json()
        except ValueError:
            raise http_exception("Unable to deserialize API response. The response was: {0}".format(response.text()))

        if "error" in response:
            raise http_exception(response["error"][1], error_code=response["error"][0])

        if "result" not in response:
            return None

        response_object = {}
        for entry in response["result"]:
            response_object.update(entry)
        return response_object
