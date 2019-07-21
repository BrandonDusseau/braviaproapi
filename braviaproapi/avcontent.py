from enum import Enum
from .errors import HttpError, BraviaApiError, ApiErrors, getErrorMessage
from .util import coalesce_none_or_empty


class InputIcon(Enum):
    UNKNOWN = 0
    COMPOSITE = 1
    SVIDEO = 2
    COMPOSITE_COMPONENTD = 3
    COMPONENTD = 4
    COMPONENT = 5
    SCART = 6
    HDMI = 7
    VGA = 8
    TUNER = 9
    TAPE = 10
    DISC = 11
    COMPLEX = 12
    AV_AMP = 13
    HOME_THEATER = 14
    GAME = 15
    CAMCORDER = 16
    DIGITAL_CAMERA = 17
    PC = 18
    TV = 19
    AUDIO_SYSTEM = 20
    RECORDING_DEVICE = 21
    PLAYBACK_DEVICE = 22
    TUNER_DEVICE = 23
    WIFI_DISPLAY = 24



class AvContent(object):
    def __init__(self, bravia_client, http_client):
        self.bravia_client = bravia_client
        self.http_client = http_client

    # NOTE: the 'type' and 'target' parameters are not implemented for this call, as Sony's documentation
    #       does not thoroughly explain what they do.
    def get_content_count(self, source=None):
        self.bravia_client.initialize()

        if type(source) is not str:
            raise TypeError("source must be a string value")

        if not source:
            raise ValueError("source must be non-empty string representing a source URI")

        try:
            response = self.http_client.request(
                endpoint="avContent",
                method="getContentCount",
                params={"source": source if source else ""},
                version="1.1"
            )
        except HttpError as err:
            raise BraviaApiError(getErrorMessage(err.error_code, str(err))) from None

        if "count" not in response or type(response["count"]) is not int:
            raise BraviaApiError("API returned unexpected response format for getContentCount")

        return response["count"]

    def get_content_list(self, source):
        self.bravia_client.initialize()

        if type(source) is not str:
            raise TypeError("source must be a string value")

        if not source:
            raise ValueError("source must be non-empty string representing a source URI")

        count = self.get_content_count(source)
        if count == 0:
            return None

        content = []

        start = 0
        while (start < count):
            try:
                response = self.http_client.request(
                    endpoint="avContent",
                    method="getContentList",
                    params={"source": source, "stIdx": start, "cnt": 50},
                    version="1.2"
                )
            except HttpError as err:
                raise BraviaApiError(getErrorMessage(err.error_code, str(err))) from None

            if not response or type(response) is not list:
                raise BraviaApiError("API returned unexpected response format for getContentList")

            for index in response:
                content.append({
                    "index": index.get("index"),
                    "name": coalesce_none_or_empty(index.get("title")),
                    "uri": coalesce_none_or_empty(index.get("uri"))
                })

            start += 50

        return content if len(content) > 0 else None

    def get_scheme_list(self):
        self.bravia_client.initialize()

        try:
            response = self.http_client.request(
                endpoint="avContent",
                method="getSchemeList",
                version="1.0"
            )
        except HttpError as err:
            raise BraviaApiError(getErrorMessage(err.error_code, str(err))) from None

        if not response or type(response) is not list:
            raise BraviaApiError("API returned unexpected response format for getSchemeList")

        schemes = []
        for scheme_entry in response:
            if scheme_entry.get("scheme") is None:
                continue

            schemes.append(scheme_entry.get("scheme"))

        return schemes

    def get_source_list(self, scheme):
        self.bravia_client.initialize()

        if type(scheme) is not str:
            raise TypeError("scheme must be a string value")

        if not scheme:
            raise ValueError("scheme must be non-empty string")

        try:
            response = self.http_client.request(
                endpoint="avContent",
                method="getSourceList",
                params={"scheme": scheme},
                version="1.0"
            )
        except HttpError as err:
            raise BraviaApiError(getErrorMessage(err.error_code, str(err))) from None

        if not response or type(response) is not list:
            raise BraviaApiError("API returned unexpected response format for getSourceList")

        sources = []
        for source_entry in response:
            if source_entry.get("source") is None:
                continue

            sources.append(source_entry.get("source"))

        return sources

    def get_external_input_status(self):
        self.bravia_client.initialize()

        try:
            response = self.http_client.request(
                endpoint="avContent",
                method="getCurrentExternalInputsStatus",
                version="1.1"
            )
        except HttpError as err:
            raise BraviaApiError(getErrorMessage(err.error_code, str(err))) from None

        if not response or type(response) is not list:
            raise BraviaApiError("API returned unexpected response format for getCurrentExternalInputsStatus")

        valid_icons = {
            "meta:composite": InputIcon.COMPOSITE,
            "meta:svideo": InputIcon.SVIDEO,
            "meta:composite_componentd": InputIcon.COMPOSITE_COMPONENTD,
            "meta:component": InputIcon.COMPONENT,
            "meta:componentd": InputIcon.COMPONENTD,
            "meta:scart": InputIcon.SCART,
            "meta:hdmi": InputIcon.HDMI,
            "meta:dsub15": InputIcon.VGA,
            "meta:tuner": InputIcon.TUNER,
            "meta:tape": InputIcon.TAPE,
            "meta:disc": InputIcon.DISC,
            "meta:complex": InputIcon.COMPLEX,
            "meta:avamp": InputIcon.AV_AMP,
            "meta:hometheater": InputIcon.HOME_THEATER,
            "meta:game": InputIcon.GAME,
            "meta:camcorder": InputIcon.CAMCORDER,
            "meta:digitalcamera": InputIcon.DIGITAL_CAMERA,
            "meta:pc": InputIcon.PC,
            "meta:tv": InputIcon.TV,
            "meta:audiosystem": InputIcon.AUDIO_SYSTEM,
            "meta:recordingdevice": InputIcon.RECORDING_DEVICE,
            "meta:playbackdevice": InputIcon.PLAYBACK_DEVICE,
            "meta:tunerdevice": InputIcon.TUNER_DEVICE,
            "meta:wifidisplay": InputIcon.WIFI_DISPLAY
        }

        inputs = []
        for entry in response:
            if entry is None:
                continue

            input = {
                "uri": coalesce_none_or_empty(entry.get("uri")),
                "name": coalesce_none_or_empty(entry.get("title")),
                "connected": True if entry.get("connection") else False,
                "custom_label": coalesce_none_or_empty(entry.get("label")),
                "icon": valid_icons.get(entry.get("icon"), InputIcon.UNKNOWN),
                "has_signal": True if entry.get("status") else False
            }
            inputs.append(input)

        return inputs

    def get_playing_content_info(self):
        self.bravia_client.initialize()

        try:
            response = self.http_client.request(
                endpoint="avContent",
                method="getPlayingContentInfo",
                version="1.0"
            )
        except HttpError as err:
            # If the display is off, there is no playing content, so return None
            if err.error_code == ApiErrors.DISPLAY_OFF.value:
                return None
            else:
                raise BraviaApiError(getErrorMessage(err.error_code, str(err))) from None

        if not response or type(response) is not dict:
            raise BraviaApiError("API returned unexpected response format for getPlayingContentInfo")

        return {
            "uri": coalesce_none_or_empty(response.get("uri")),
            "source": coalesce_none_or_empty(response.get("source")),
            "name": coalesce_none_or_empty(response.get("title"))
        }

    def set_play_content(self, uri):
        self.bravia_client.initialize()

        if type(uri) is not str:
            raise TypeError("uri must be a string value")

        if not uri:
            raise ValueError("uri must be non-empty string")

        try:
            response = self.http_client.request(
                endpoint="avContent",
                method="setPlayContent",
                params={"uri": uri},
                version="1.0"
            )
        except HttpError as err:
            raise BraviaApiError(getErrorMessage(err.error_code, str(err))) from None

        if not response or type(response) is not dict:
            raise BraviaApiError("API returned unexpected response format for getPlayingContentInfo")
