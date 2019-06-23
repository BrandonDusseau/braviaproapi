from enum import Enum
from .errors import HttpError, BraviaApiError


# These are some defaults specified by Sony
class ButtonCode(Enum):
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
    def __init__(self, bravia_client, http_client):
        self.bravia_client = bravia_client
        self.http_client = http_client

    def send_button(self, button):
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
            raise BraviaApiError("An unexpected error occurred: {0}".format(str(err)))
