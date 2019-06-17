from enum import Enum
from .errors import HttpError, BraviaApiError
from .util import coalesce_none_or_empty


# Error code definitions
class ErrorCode(object):
    ILLEGAL_ARGUMENT = 3
    ERR_CLOCK_NOT_SET = 7
    ILLEGAL_STATE = 7
    ENCRYPTION_ERROR = 40002
    CLIENT_MUST_WAIT = 40003


class AppFeature(Enum):
    UNKNOWN = 0
    TEXT_INPUT = 1
    CURSOR_DISPLAY = 2
    WEB_BROWSE = 3


class AppControl(object):
    def __init__(self, bravia_client, http_client):
        self.bravia_client = bravia_client
        self.http_client = http_client

    def get_application_list(self, exclude_builtin=False):
        self.bravia_client.initialize()

        if type(exclude_builtin) is not bool:
            raise TypeError("exclude_builtin must be a boolean type")

        response = self.http_client.request(endpoint="appControl", method="getApplicationList", version="1.0")

        apps = []
        if response is None:
            return apps

        if type(response) is not list:
            raise BraviaApiError("API returned unexpected response format for getApplicationList")

        for app_info in response:
            app = {
                "name": coalesce_none_or_empty(app_info.get("title")),
                "uri": coalesce_none_or_empty(app_info.get("uri")),
                "icon": coalesce_none_or_empty(app_info.get("icon"))
            }

            if exclude_builtin and app["uri"] is not None and "com.sony.dtv.ceb" in app["uri"]:
                continue

            apps.append(app)

        return apps

    def get_application_feature_status(self):
        self.bravia_client.initialize()

        response = self.http_client.request(endpoint="appControl", method="getApplicationStatusList", version="1.0")

        if type(response) is not list:
            raise BraviaApiError("API returned unexpected response format for getApplicationStatusList")

        supported_features = {
            "textInput": AppFeature.TEXT_INPUT,
            "cursorDisplay": AppFeature.CURSOR_DISPLAY,
            "webBrowse": AppFeature.WEB_BROWSE
        }

        enabled_features = {
            AppFeature.TEXT_INPUT: False,
            AppFeature.CURSOR_DISPLAY: False,
            AppFeature.WEB_BROWSE: False
        }

        for feature in response:
            feature_type = supported_features.get(feature["name"], AppFeature.UNKNOWN)

            # Skip unsupported features
            if feature_type == AppFeature.UNKNOWN:
                continue

            enabled_features[feature_type] = True if feature["status"] == "on" else False

        return enabled_features

    def get_text_form(self):
        self.bravia_client.initialize()

        encrypted_key = self.bravia_client.encryption.get_rsa_encrypted_common_key()

        if encrypted_key is None:
            raise BraviaApiError(
                "This device does not support the appropriate encryption needed to access text fields."
            )

        try:
            response = self.http_client.request(
                endpoint="appControl",
                method="getTextForm",
                params={"encKey": encrypted_key},
                version="1.1"
            )
        except HttpError as err:
            if err.error_code == ErrorCode.CLIENT_MUST_WAIT or err.error_code == ErrorCode.ILLEGAL_STATE:
                return None
            elif err.error_code == ErrorCode.ENCRYPTION_ERROR:
                raise BraviaApiError("Internal error: The target device rejected our encryption key")
            else:
                raise err

        if "text" not in response:
            raise BraviaApiError("API returned unexpected response format for getTextForm")

        decrypted_text = self.bravia_client.encryption.aes_decrypt_b64(response["text"])

        return decrypted_text

    def get_web_app_status(self):
        self.bravia_client.initialize()

        try:
            response = self.http_client.request(endpoint="appControl", method="getWebAppStatus", version="1.0")
        except HttpError as err:
            if err.error_code == ErrorCode.ILLEGAL_STATE:
                raise BraviaApiError("The target device must be powered on to get web app status")
            else:
                raise err

        return {
            "active": True if response.get("active") == "true" else False,
            "url": coalesce_none_or_empty(response.get("url"))
        }
