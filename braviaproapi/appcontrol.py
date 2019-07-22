from enum import Enum
from .errors import HttpError, BraviaApiError, BraviaAppLaunchAlreadyInProgressError, \
    BraviaInternalError, BraviaAppLaunchError, BraviaNoFocusedTextFieldError, ApiErrors, get_error_message
from .util import coalesce_none_or_empty


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
            feature_type = supported_features.get(feature.get("name"), AppFeature.UNKNOWN)

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
            if err.error_code == ApiErrors.CLIENT_MUST_WAIT.value or err.error_code == ApiErrors.ILLEGAL_STATE.value:
                return None
            elif err.error_code == ApiErrors.ENCRYPTION_ERROR.value:
                raise BraviaInternalError("Internal error: The target device rejected our encryption key")
            else:
                raise BraviaApiError(get_error_message(err.error_code, str(err))) from None

        if "text" not in response:
            raise BraviaApiError("API returned unexpected response format for getTextForm")

        decrypted_text = self.bravia_client.encryption.aes_decrypt_b64(response["text"])

        return decrypted_text

    def get_web_app_status(self):
        self.bravia_client.initialize()

        try:
            response = self.http_client.request(endpoint="appControl", method="getWebAppStatus", version="1.0")
        except HttpError as err:
            raise BraviaApiError(get_error_message(err.error_code, str(err))) from None

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
            if err.error_code == ApiErrors.ANOTHER_REQUEST_IN_PROGRESS.value:
                raise BraviaAppLaunchError(
                    "Another app is currently in the process of launching"
                )
            elif err.error_code == ApiErrors.FAILED_TO_LAUNCH.value:
                raise BraviaAppLaunchError("The app failed to launch")
            elif err.error_code == ApiErrors.REQUEST_IN_PROGRESS.value:
                # This is actually a success message, so ignore it
                pass
            else:
                raise BraviaApiError(get_error_message(err.error_code, str(err))) from None

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
            if err.error_code == ApiErrors.ILLEGAL_STATE.value:
                raise BraviaNoFocusedTextFieldError(
                    "The target device does not currently have a writable text field focused."
                )
            elif err.error_code == ApiErrors.ENCRYPTION_FAILED.value:
                raise BraviaInternalError("Internal error: The target device rejected our encryption key")
            else:
                raise BraviaApiError(get_error_message(err.error_code, str(err))) from None

    def terminate_all_apps(self):
        self.bravia_client.initialize()

        try:
            self.http_client.request(endpoint="appControl", method="terminateApps", version="1.0")
        except HttpError as err:
            if err.error_code == ApiErrors.FAILED_TO_TERMINATE.value:
                # Some apps may not be allowed to be terminated. This is an expected response in that case.
                pass
            else:
                raise BraviaApiError(get_error_message(err.error_code, str(err))) from None
