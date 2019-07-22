from enum import Enum
from .errors import HttpError, BraviaApiError, BraviaInternalError, BraviaInvalidStateError, ApiErrors, \
    get_error_message


class SceneMode(Enum):
    UNKNOWN = 0
    AUTO = 1
    AUTO_24P_SYNC = 2
    GENERAL = 3


class VideoScreen(object):
    def __init__(self, bravia_client, http_client):
        self.bravia_client = bravia_client
        self.http_client = http_client

    def set_scene_setting(self, setting):
        self.bravia_client.initialize()

        if type(setting) is not SceneMode:
            raise TypeError("setting must be a SceneMode enum value")

        if setting == SceneMode.UNKNOWN:
            raise ValueError("setting cannot be SceneMode.UNKNOWN")

        modes = {
            SceneMode.AUTO: "auto",
            SceneMode.AUTO_24P_SYNC: "auto24pSync",
            SceneMode.GENERAL: "general"
        }
        sent_mode = modes.get(setting, SceneMode.UNKNOWN)

        if sent_mode == SceneMode.UNKNOWN:
            raise BraviaInternalError("Internal error: Unsupported SceneMode selected")

        try:
            self.http_client.request(
                endpoint="videoScreen",
                method="setSceneSetting",
                params={"value": sent_mode},
                version="1.0"
            )
        except HttpError as err:
            if err.error_code == ApiErrors.ILLEGAL_ARGUMENT.value:
                raise BraviaInternalError("Internal error: an invalid argument was sent to the API")
            elif err.error_code == ApiErrors.ILLEGAL_STATE.value:
                raise BraviaInvalidStateError(
                    ("Either the target device is powered off or it does not support the selected SceneMode for the"
                     + " current input")
                )
            else:
                raise BraviaApiError(get_error_message(err.error_code, str(err))) from None
