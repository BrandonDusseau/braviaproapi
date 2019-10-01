from enum import Enum
from .errors import HttpError, ApiError, InternalError, AppLaunchError, NoFocusedTextFieldError, \
    ErrorCode, get_error_message, EncryptionError
from .util import coalesce_none_or_empty


class AppFeature(Enum):
    '''
    Describes which features are supported by the current app.

    Attributes:
        UNKNOWN: The app feature was not recognized.
        TEXT_INPUT: The app has a text field focused.
        CURSOR_DISPLAY: The app has a cursor displayed.
        WEB_BROWSE: The app is using an embedded web browser.
    '''
    UNKNOWN = 0
    TEXT_INPUT = 1
    CURSOR_DISPLAY = 2
    WEB_BROWSE = 3


class AppControl(object):
    '''
    Provides functionality for interacting with applications on the target device.

    Args:
        bravia_client: The parent :class:`BraviaClient` instance.
        http_client: The :class:`Http` instance associated with the parent client.
    '''

    def __init__(self, bravia_client, http_client):
        self.bravia_client = bravia_client
        self.http_client = http_client

    def get_application_list(self, exclude_builtin=False):
        '''
        Retrieves a list of applications installed on the target device.

        Args:
            exclude_builtin (bool): If True, excludes built-in Sony applications which are not exposed on the\
                                    home screen.

        Raises:
            TypeError: One or more arguments is the incorrect type.
            ApiError: The request to the target device failed.

        Returns:
            list(dict): A list of dicts containing the following properties:

            * name (`str or None`): The display name of the application.
            * uri (`str or None`): The internal URI at which the application can be accessed, used when referring to\
                the app from other functions.
            * icon (`str or None`): A network URL pointing to the application's icon image.
        '''

        self.bravia_client.initialize()

        if type(exclude_builtin) is not bool:
            raise TypeError("exclude_builtin must be a boolean type")

        response = self.http_client.request(endpoint="appControl", method="getApplicationList", version="1.0")

        apps = []
        if response is None:
            return apps

        if type(response) is not list:
            raise ApiError("API returned unexpected response format for getApplicationList")

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
        '''
        Determines which features are supported by the currently running application on the target device.

        Raises:
            ApiError: The request to the target device failed.

        Returns:
            dict: A dict with the following keys with boolean values:

            * textInput (`bool`): True if the application currently has a text input focused.
            * cursorDisplay (`bool`): True if the application currently has an interactive cursor.
            * webBrowse (`bool`): True if the application currently has a web browser displayed.
        '''

        self.bravia_client.initialize()

        try:
            response = self.http_client.request(endpoint="appControl", method="getApplicationStatusList", version="1.0")
        except HttpError as err:
            raise ApiError(get_error_message(err.error_code, str(err))) from None

        if type(response) is not list:
            raise ApiError("API returned unexpected response format for getApplicationStatusList")

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
        '''
        Decrypts and returns the contents of the text field focused on the target device.

        Raises:
            InternalError: The target device was unable to encrypt the text.
            ApiError: The request to the target device failed.
            EncryptionError: The target device could not provide a valid encryption key.

        Returns:
            str or None: The text, or `None` if no text field is currently focused.
        '''

        self.bravia_client.initialize()

        encrypted_key = self.bravia_client.encryption.get_rsa_encrypted_common_key()

        if encrypted_key is None:
            raise EncryptionError(
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
            # These errors likely indicate there is no focused text field, so return None
            if err.error_code == ErrorCode.REQUEST_DUPLICATED.value or err.error_code == ErrorCode.ILLEGAL_STATE.value:
                return None
            elif err.error_code == ErrorCode.ENCRYPTION_ERROR.value:
                raise InternalError("Internal error: The target device rejected our encryption key")
            else:
                raise ApiError(get_error_message(err.error_code, str(err))) from None

        if "text" not in response:
            raise ApiError("API returned unexpected response format for getTextForm")

        decrypted_text = self.bravia_client.encryption.aes_decrypt_b64(response["text"])

        return decrypted_text

    def get_web_app_status(self):
        '''
        Returns information about the web application currently in use on the target device.

        Raises:
            ApiError: The request to the target device failed.

        Returns:
            dict: A dict containing the following keys:

            * active (`bool`): True if there is currently a web application running on the target device.
            * url (`str or None`): The URL of the application currently running, None if no such app is running.
        '''

        self.bravia_client.initialize()

        try:
            response = self.http_client.request(endpoint="appControl", method="getWebAppStatus", version="1.0")
        except HttpError as err:
            raise ApiError(get_error_message(err.error_code, str(err))) from None

        return {
            "active": True if response.get("active") == "true" else False,
            "url": coalesce_none_or_empty(response.get("url"))
        }

    def set_active_app(self, uri):
        '''
        Opens the specified app on the target device.

        Args:
            uri (str): The URI of the application to open (acquired using :func:`get_application_list()`)

        Raises:
            TypeError: One or more arguments is the incorrect type.
            AppLaunchError: The application could not be opened.
            ApiError: The request to the target device failed.
        '''

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
            if err.error_code == ErrorCode.ANOTHER_REQUEST_IN_PROGRESS.value:
                raise AppLaunchError(
                    "Another app is currently in the process of launching"
                )
            elif err.error_code == ErrorCode.FAILED_TO_LAUNCH.value:
                raise AppLaunchError("The app failed to launch")
            elif err.error_code == ErrorCode.REQUEST_IN_PROGRESS.value:
                # This is actually a success message, so ignore it
                pass
            else:
                raise ApiError(get_error_message(err.error_code, str(err))) from None

    def set_text_form(self, text):
        '''
        Enters the specified text in the focused text field on the target device.
        Text is encrypted before being sent to the device.

        Args:
            text (str): The text to input.

        Raises:
            TypeError: One or more arguments is the incorrect type.
            ApiError: The request to the device failed.
            EncryptionError: The target device could not provide a valid encryption key.
            NoFocusedTextFieldError: There is no text field to input text to on the target device.
            InternalError: The target device failed to decrypt the text.
        '''

        self.bravia_client.initialize()

        if type(text) is not str:
            raise TypeError("text must be a string type")

        encrypted_key = self.bravia_client.encryption.get_rsa_encrypted_common_key()

        if encrypted_key is None:
            raise EncryptionError(
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
            if err.error_code == ErrorCode.ILLEGAL_STATE.value:
                raise NoFocusedTextFieldError(
                    "The target device does not currently have a writable text field focused."
                )
            elif err.error_code == ErrorCode.ENCRYPTION_FAILED.value:
                raise InternalError("Internal error: The target device rejected our encryption key. This is a bug.")
            else:
                raise ApiError(get_error_message(err.error_code, str(err))) from None

    def terminate_all_apps(self):
        '''
        Instructs the target device to terminate all running applications.

        Raises:
            ApiError: The request to the target device failed.
        '''

        self.bravia_client.initialize()

        try:
            self.http_client.request(endpoint="appControl", method="terminateApps", version="1.0")
        except HttpError as err:
            if err.error_code == ErrorCode.FAILED_TO_TERMINATE.value:
                # Some apps may not be allowed to be terminated. This is an expected response in that case.
                pass
            else:
                raise ApiError(get_error_message(err.error_code, str(err))) from None
