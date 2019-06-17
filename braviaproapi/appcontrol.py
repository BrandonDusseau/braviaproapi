from enum import Enum
from .errors import HttpError, BraviaApiError, BraviaAppLaunchAlreadyInProgressError, \
    BraviaAppLaunchError, BraviaNoFocusedTextFieldError
from .util import coalesce_none_or_empty


# Error code definitions
class ErrorCode(object):
    ILLEGAL_ARGUMENT = 3
    ERR_CLOCK_NOT_SET = 7
    ILLEGAL_STATE = 7
    ENCRYPTION_ERROR = 40002
    CLIENT_MUST_WAIT = 40003
    APP_REQUEST_ALREADY_PROCESSING = 41400
    APP_FAILED_TO_LAUNCH = 41401
    APP_LAUNCH_IN_PROGRESS = 41402
    APP_FAILED_TO_TERMINATE = 41403


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
                raise BraviaApiError("An unexpected error occurred: {0}".format(str(err)))

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
                raise BraviaApiError("An unexpected error occurred: {0}".format(str(err)))

        return {
            "active": True if response.get("active") == "true" else False,
            "url": coalesce_none_or_empty(response.get("url"))
        }

    def set_active_app(self, uri):
        self.bravia_client.initialize()

        if type(uri) is not str:
            raise TypeError("uri must be a string type")

        try:
            self.http_client.request(
                endpoint="appControl",
                method="setActiveApp",
                params={"uri": uri},
                version="1.0"
            )
        except HttpError as err:
            if err.error_code == ErrorCode.APP_REQUEST_ALREADY_PROCESSING:
                raise BraviaAppLaunchAlreadyInProgressError(
                    "Another app is currently in the process of launching"
                )
            elif err.error_code == ErrorCode.APP_FAILED_TO_LAUNCH:
                raise BraviaAppLaunchError("The app failed to launch")
            elif err.error_code == ErrorCode.APP_LAUNCH_IN_PROGRESS:
                # This is actually a success message, so ignore it
                pass
            else:
                raise BraviaApiError("An unexpected error occurred: {0}".format(str(err)))

    def set_text_form(self, text):
        self.bravia_client.initialize()

        if type(text) is not str:
            raise TypeError("text must be a string type")

        encrypted_key = self.bravia_client.encryption.get_rsa_encrypted_common_key()

        if encrypted_key is None:
            raise BraviaApiError(
                "This device does not support the appropriate encryption needed to access text fields."
            )

        encrypted_text = self.bravia_client.encryption.aes_encrypt_b64(text)

        try:
            self.http_client.request(
                endpoint="appControl",
                method="setTextForm",
                params={"encKey": encrypted_key, "text": encrypted_text},
                version="1.1"
            )
        except HttpError as err:
            if err.error_code == ErrorCode.ILLEGAL_STATE:
                raise BraviaNoFocusedTextFieldError(
                    "The target device does not currently have a writable text field focused."
                )
            elif err.error_code == ErrorCode.ENCRYPTION_ERROR:
                raise BraviaApiError("Internal error: The target device rejected our encryption key")
            else:
                raise BraviaApiError("An unexpected error occurred: {0}".format(str(err)))

    def terminate_all_apps(self):
        self.bravia_client.initialize()

        try:
            self.http_client.request(endpoint="appControl", method="terminateApps", version="1.0")
        except HttpError as err:
            if err.error_code == ErrorCode.APP_FAILED_TO_TERMINATE:
                # Some apps may not be allowed to be terminated. This is an expected response in that case.
                pass
            else:
                raise BraviaApiError("An unexpected error occurred: {0}".format(str(err)))
