import json
import requests
from .errors import HttpError


class Http(object):
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
            request_params.append(params)

        payload = {
            "method": method,
            "params": request_params,
            "version": version,
            "id": self.request_id
        }

        try:
            result = requests.post(url, headers=headers, data=json.dumps(payload), timeout=5)
        except requests.exceptions.Timeout:
            raise HttpError("The request timed out. Is the device powered with the IP control interface enabled?")
        except requests.exceptions.ConnectionError as err:
            raise HttpError("A connection error occurred: {0}".format(str(err)))
        except requests.exceptions.RequestsException as err:
            raise HttpError("An unexpected error occurred while sending the request: {0}".format(str(err)))

        if result.status_code != 200:
            raise HttpError("Unexpected status code {0} received".format(str(result.status_code)))

        try:
            response = result.json()
        except ValueError:
            raise HttpError("Unable to deserialize API response. The response was: {0}".format(response.text()))

        if "error" in response:
            raise HttpError(
                "{0} (error {1})".format(response["error"][1], response["error"][0]),
                error_code=response["error"][0]
            )

        if "result" not in response:
            raise HttpError("The API response was malformed")

        # The API's response is encapsulated in an array, so extract and return it
        if not isinstance(response["result"], list):
            raise ValueError("The API response was in an unexpected format and cannot be processed.")
        if len(response["result"]) == 0:
            return None
        elif len(response["result"]) > 1:
            return response["result"]
        else:
            return response["result"][0]

    def remote_request(self, remote_code):
        url = "http://{0}/sony/ircc".format(self.host)
        headers = {
            "X-Auth-PSK": self.psk,
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
            "SOAPACTION": "\"urn:schemas-sony-com:service:IRCC:1#X_SendIRCC\"",
            "Content-Type": "application/xml; charset=UTF-8",
            "Accept": "*/*"
        }

        request = (
            ("<s:Envelope\n"
                "    xmlns:s=\"http://schemas.xmlsoap.org/soap/envelope/\"\n"
                "    s:encodingStyle=\"http://schemas.xmlsoap.org/soap/encoding/\">\n"
                "    <s:Body>\n"
                "        <u:X_SendIRCC xmlns:u=\"urn:schemas-sony-com:service:IRCC:1\">\n"
                "            <IRCCCode>{0}</IRCCCode>\n"
                "        </u:X_SendIRCC>\n"
                "    </s:Body>\n"
                "</s:Envelope>\n").format(remote_code)
        )

        try:
            result = requests.post(url, headers=headers, data=request, timeout=5)
        except requests.exceptions.Timeout:
            raise HttpError("The request timed out. Is the device powered with the IRCC interface enabled?")
        except requests.exceptions.ConnectionError as err:
            raise HttpError("A connection error occurred: {0}".format(str(err)))
        except requests.exceptions.RequestsException as err:
            raise HttpError("An unexpected error occurred while sending the request: {0}".format(str(err)))

        if result.status_code != 200:
            raise HttpError("Unexpected status code {0} received".format(str(result.status_code)))
