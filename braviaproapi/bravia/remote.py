from enum import Enum
from .errors import HttpError, ApiError, get_error_message


# These are some defaults specified by Sony
class ButtonCode(Enum):
    '''
    Describes the default button codes for the IRCC remote control interface.

    Attributes:
        POWER: Power on/off
        INPUT: Change input source
        SYNC_MENU: Open the Bravia Sync menu
        HDMI_1: Switch to HDMI 1 source
        HDMI_2: Switch to HDMI 2 source
        HDMI_3: Switch to HDMI 3 source
        HDMI_4: Switch to HDMI 4 source
        NUM_1: '1' key
        NUM_2: '2' key
        NUM_3: '3' key
        NUM_4: '4' key
        NUM_5: '5' key
        NUM_6: '6' key
        NUM_7: '7' key
        NUM_8: '8' key
        NUM_9: '9' key
        NUM_0: '0' key
        DOT: '.' or '-' key used for tuner subchannels
        CAPTION: Set closed captioning mode
        RED: Red favorite key
        GREEN: Green favorite key
        YELLOW: Yellow favorite key
        BLUE: Blue favorite key
        UP: Up directional key
        DOWN: Down directional key
        RIGHT: Right directional key
        LEFT: Left directional key
        CONFIRM: Confirm/OK key
        HELP: Opens system help
        DISPLAY: Opens display options
        OPTIONS: Opens options menu (Action Menu)
        BACK: Returns to previous screen
        HOME: Goes to home screen
        VOLUME_UP: Increase volume by one unit
        VOLUME_DOWN: Decrease volume by one unit
        MUTE: Mute audio
        AUDIO: Switch audio mode
        CHANNEL_UP: Go to next TV channel
        CHANNEL_DOWN: Go to previous TV channel
        PLAY: Play content
        STOP: Stop content
        FLASH_PLUS: Fast forward
        FLASH_MINUS: Rewind
        PREV: Go to previous track
        NEXT: Go to next track

    '''
    POWER = "AAAAAQAAAAEAAAAVAw=="
    INPUT = "AAAAAQAAAAEAAAAlAw=="
    SYNC_MENU = "AAAAAgAAABoAAABYAw=="
    HDMI_1 = "AAAAAgAAABoAAABaAw=="
    HDMI_2 = "AAAAAgAAABoAAABbAw=="
    HDMI_3 = "AAAAAgAAABoAAABcAw=="
    HDMI_4 = "AAAAAgAAABoAAABdAw=="
    NUM_1 = "AAAAAQAAAAEAAAAAAw=="
    NUM_2 = "AAAAAQAAAAEAAAABAw=="
    NUM_3 = "AAAAAQAAAAEAAAACAw=="
    NUM_4 = "AAAAAQAAAAEAAAADAw=="
    NUM_5 = "AAAAAQAAAAEAAAAEAw=="
    NUM_6 = "AAAAAQAAAAEAAAAFAw=="
    NUM_7 = "AAAAAQAAAAEAAAAGAw=="
    NUM_8 = "AAAAAQAAAAEAAAAHAw=="
    NUM_9 = "AAAAAQAAAAEAAAAIAw=="
    NUM_0 = "AAAAAQAAAAEAAAAJAw=="
    DOT = "AAAAAgAAAJcAAAAdAw=="
    CAPTION = "AAAAAgAAAJcAAAAoAw=="
    RED = "AAAAAgAAAJcAAAAlAw=="
    GREEN = "AAAAAgAAAJcAAAAmAw=="
    YELLOW = "AAAAAgAAAJcAAAAnAw=="
    BLUE = "AAAAAgAAAJcAAAAkAw=="
    UP = "AAAAAQAAAAEAAAB0Aw=="
    DOWN = "AAAAAQAAAAEAAAB1Aw=="
    RIGHT = "AAAAAQAAAAEAAAAzAw=="
    LEFT = "AAAAAQAAAAEAAAA0Aw=="
    CONFIRM = "AAAAAQAAAAEAAABlAw=="
    HELP = "AAAAAgAAAMQAAABNAw=="
    DISPLAY = "AAAAAQAAAAEAAAA6Aw=="
    OPTIONS = "AAAAAgAAAJcAAAA2Aw=="
    BACK = "AAAAAgAAAJcAAAAjAw=="
    HOME = "AAAAAQAAAAEAAABgAw=="
    VOLUME_UP = "AAAAAQAAAAEAAAASAw=="
    VOLUME_DOWN = "AAAAAQAAAAEAAAATAw=="
    MUTE = "AAAAAQAAAAEAAAAUAw=="
    AUDIO = "AAAAAQAAAAEAAAAXAw=="
    CHANNEL_UP = "AAAAAQAAAAEAAAAQAw=="
    CHANNEL_DOWN = "AAAAAQAAAAEAAAARAw=="
    PLAY = "AAAAAgAAAJcAAAAaAw=="
    PAUSE = "AAAAAgAAAJcAAAAZAw=="
    STOP = "AAAAAgAAAJcAAAAYAw=="
    FLASH_PLUS = "AAAAAgAAAJcAAAB4Aw=="
    FLASH_MINUS = "AAAAAgAAAJcAAAB5Aw=="
    PREV = "AAAAAgAAAJcAAAA8Aw=="
    NEXT = "AAAAAgAAAJcAAAA9Aw=="


class Remote(object):
    '''
    Provides remote control functionality for the target device.

    Args:
        bravia_client: The parent :class:`BraviaClient` instance.
        http_client: The :class:`Http` instance associated with the parent client.
    '''

    def __init__(self, bravia_client, http_client):
        self.bravia_client = bravia_client
        self.http_client = http_client

    def send_button(self, button):
        '''
        Sends a remote control button press to the target device. Button codes can come from the predefined ButtonCode
        enum, or :func:`System.get_remote_control_info()` can return a device-specific list.

        Args:
            button (ButtonCode or str): The button code to send.

        Raises:
            TypeError: One or more arguments is the incorrect type.
            ApiError: The request to the target device failed.
        '''

        self.bravia_client.initialize()

        if type(button) is ButtonCode:
            button_code = button.value
        elif type(button) is str:
            button_code = button
        else:
            raise TypeError("button must be a ButtonCode enum or string value")

        try:
            self.http_client.remote_request(button_code)
        except HttpError as err:
            raise ApiError(get_error_message(err.error_code, str(err))) from None
