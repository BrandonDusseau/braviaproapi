from enum import Enum
from .errors import HttpError, ApiError, InternalError, InvalidStateError, ErrorCode, get_error_message


class SceneMode(Enum):
    '''
    Specifies the screen mode of the target device.

    Attributes:
        UNKNOWN: The screen mode was not recognized.
        AUTO: Automatically sets the scene based on content.
        AUTO_24P_SYNC: Automatically selects "Cinema" mode for 24Hz content, otherwise same as AUTO.
        GENERAL: Turns off scene select.
    '''
    UNKNOWN = 0
    AUTO = 1
    AUTO_24P_SYNC = 2
    GENERAL = 3


class VideoScreen(object):
    '''
    Provides functionality for configuring the target device's display.

    Args:
        bravia_client: The parent :class:`BraviaClient` instance.
        http_client: The :class:`Http` instance associated with the parent client.
    '''

    def __init__(self, bravia_client, http_client):
        self.bravia_client = bravia_client
        self.http_client = http_client

    def set_scene_setting(self, setting):
        '''
        Sets the scene mode for the display.

        Args:
            setting (SceneMode): The scene mode to set. May not be `SceneMode.UNKNOWN`.

        Raises:
            TypeError: One or more arguments is the incorrect type.
            ValueError: One or more arguments is invalid.
            ApiError: The request to the target device failed.
            InvalidStateError: The target device is off or does not support this mode for the current input.
            InternalError: An internal error occurred.
        '''

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
            raise InternalError("Internal error: Unsupported SceneMode selected")

        try:
            self.http_client.request(
                endpoint="videoScreen",
                method="setSceneSetting",
                params={"value": sent_mode},
                version="1.0"
            )
        except HttpError as err:
            if err.error_code == ErrorCode.ILLEGAL_ARGUMENT.value:
                raise InternalError("Internal error: an invalid argument was sent to the API")
            elif err.error_code == ErrorCode.ILLEGAL_STATE.value:
                raise InvalidStateError(
                    ("Either the target device is powered off or it does not support the selected SceneMode for the"
                        " current input")
                )
            else:
                raise ApiError(get_error_message(err.error_code, str(err))) from None
