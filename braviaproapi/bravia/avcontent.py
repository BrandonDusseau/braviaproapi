from enum import Enum
from .errors import HttpError, ApiError, ErrorCode, get_error_message
from .util import coalesce_none_or_empty


class InputIcon(Enum):
    '''
    Describes icon types for input sources.

    Attributes:
        UNKNOWN: The icon type was not recognized.
        COMPOSITE: Composite input
        SVIDEO: S-Video input
        COMPOSITE_COMPONENTD: Japanese D-terminal composite/component input
        COMPONENTD: Japanese D-terminal component input
        COMPONENT: Component (YPbPr) input
        SCART: SCART RGB input
        HDMI: HDMI input
        VGA: VGA D-sub input
        TUNER: Coaxial TV tuner input
        TAPE: Tape input
        DISC: Disc input
        COMPLEX: Complex input
        AV_AMP: Audio amplifier input
        HOME_THEATER: Home theater system input
        GAME: Video game input
        CAMCORDER: Camcorder input
        DIGITAL_CAMERA: Digital camera input
        PC: Computer input
        TV: Television input
        AUDIO_SYSTEM: Audio system input
        RECORDING_DEVICE: Recorder device input
        PLAYBACK_DEVICE: Player device input
        TUNER_DEVICE: Television tuner device input
        WIFI_DISPLAY: Wi-Fi display input
    '''
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
    '''
    Provides functionality for controlling what is played on the target device.

    Args:
        bravia_client: The parent :class:`BraviaClient` instance.
        http_client: The :class:`Http` instance associated with the parent client.
    '''

    def __init__(self, bravia_client, http_client):
        self.bravia_client = bravia_client
        self.http_client = http_client

    # NOTE: the 'type' and 'target' parameters are not implemented for this call, as Sony's documentation
    #       does not thoroughly explain what they do.
    def get_content_count(self, source):
        '''
        Returns a count of the number of available contents for a given source.

        Args:
            - source (str): The URI of the source to enumerate. See the `Sony documentation`__ for more information.

        .. _SonyDoc: https://pro-bravia.sony.net/develop/integrate/rest-api/spec/resource-uri-list/
        __ SonyDoc_

        Raises:
            TypeError: One or more arguments is the incorrect type.
            ValueError: One or more arguments is invalid.
            ApiError: The request to the target device failed.

        Returns:
            int: The count of available content.
        '''

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
            # Illegal argument likely implies a source type that does not exist, so return 0
            if err.error_code == ErrorCode.ILLEGAL_ARGUMENT.value:
                return 0
            else:
                raise ApiError(get_error_message(err.error_code, str(err))) from None

        if "count" not in response or type(response["count"]) is not int:
            raise ApiError("API returned unexpected response format for getContentCount")

        return int(response["count"])

    def get_content_list(self, source):
        '''
        Returns a list of available content for a given source.

        Args:
            - source (str): The URI of the source to enumerate. See the `Sony documentation`__ for more information.

        .. _SonyDoc: https://pro-bravia.sony.net/develop/integrate/rest-api/spec/resource-uri-list/
        __ SonyDoc_

        Raises:
            TypeError: One or more arguments is the incorrect type.
            ValueError: One or more arguments is invalid.
            ApiError: The request to the target device failed.

        Returns:
            list(dict) or None: A list of dicts containing the following keys. If no content is available, returns\
                               `None`.

            * index (`str`): The position of the content in the list.
            * name (`str or None`): The title of the content, if applicable.
            * uri (`str or None`): The URI at which the content can be accessed, if applicable.
        '''
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
                # Illegal argument likely implies a source type that does not exist, so return None
                if err.error_code == ErrorCode.ILLEGAL_ARGUMENT.value:
                    return None
                else:
                    raise ApiError(get_error_message(err.error_code, str(err))) from None

            if not response or type(response) is not list:
                raise ApiError("API returned unexpected response format for getContentList")

            for index in response:
                content.append({
                    "index": index.get("index"),
                    "name": coalesce_none_or_empty(index.get("title")),
                    "uri": coalesce_none_or_empty(index.get("uri"))
                })

            start += 50

        return content if len(content) > 0 else None

    def get_scheme_list(self):
        '''
        Returns a list of available content schemes the target device supports.

        Raises:
            ApiError: The request to the target device failed.

        Returns:
            list(str): A list of string names of available schemes.
        '''
        self.bravia_client.initialize()

        try:
            response = self.http_client.request(
                endpoint="avContent",
                method="getSchemeList",
                version="1.0"
            )
        except HttpError as err:
            raise ApiError(get_error_message(err.error_code, str(err))) from None

        if not response or type(response) is not list:
            raise ApiError("API returned unexpected response format for getSchemeList")

        schemes = []
        for scheme_entry in response:
            if scheme_entry.get("scheme") is None:
                continue

            schemes.append(scheme_entry.get("scheme"))

        return schemes

    def get_source_list(self, scheme):
        '''
        Returns a list of available source types for a given content scheme.

        Args:
            scheme (str): The scheme for which to get sources (retrieve this from :func:`get_scheme_list()`).

        Raises:
            TypeError: One or more arguments is the incorrect type.
            ValueError: One or more arguments is invalid.
            ApiError: The request to the target device failed.

        Returns:
            list(str) or None: A list of string source URIs for the specified scheme. If scheme is not supported,\
                               returns `None`.
        '''

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
            # Illegal argument likely implies a scheme type that does not exist, so return None
            if err.error_code == ErrorCode.ILLEGAL_ARGUMENT.value:
                return None
            else:
                raise ApiError(get_error_message(err.error_code, str(err))) from None

        if not response or type(response) is not list:
            raise ApiError("API returned unexpected response format for getSourceList")

        sources = []
        for source_entry in response:
            if source_entry.get("source") is None:
                continue

            sources.append(source_entry.get("source"))

        return sources

    def get_external_input_status(self):
        '''
        Returns information about the target device's external inputs.

        Raises:
            ApiError: The request to the target device failed.

        Returns:
            list(dict): A list of dicts with the following keys:

            * uri (`str or None`): The URI at which the input can be accessed, if applicable.
            * name (`str or None`): The system title of the input, if applicable.
            * connected (`bool`): True if the input is currently connected, False otherwise.
            * custom_label (`str or None`): The user-entered title of the input, if set.
            * icon (:class:`InputIcon`): The icon for the input. If no appropriate icon is available, this is\
                                         `InputIcon.UNKNOWN`.
            * has_signal (`bool`): True if input is currently sending a signal to the target device, False otherwise.
        '''

        self.bravia_client.initialize()

        try:
            response = self.http_client.request(
                endpoint="avContent",
                method="getCurrentExternalInputsStatus",
                version="1.1"
            )
        except HttpError as err:
            raise ApiError(get_error_message(err.error_code, str(err))) from None

        if not response or type(response) is not list:
            raise ApiError("API returned unexpected response format for getCurrentExternalInputsStatus")

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
        '''
        Returns information about the currently playing content on the target device.

        Raises:
            ApiError: The request to the target device failed.

        Returns:
            dict or None: A dict containing the following keys. If no content is playing, returns `None`.

            * uri (`str or None`): The URI at which the content can be accessed, if applicable.
            * source (`str or None`): The source that the content resides within, if applicable.
            * name (`str or None`): The title of the playing content, if applicable.
        '''

        self.bravia_client.initialize()

        try:
            response = self.http_client.request(
                endpoint="avContent",
                method="getPlayingContentInfo",
                version="1.0"
            )
        except HttpError as err:
            # The device can't return information for some types of content, or when the display is off.
            if err.error_code == ErrorCode.DISPLAY_OFF.value or err.error_code == ErrorCode.ILLEGAL_STATE.value:
                return None
            else:
                raise ApiError(get_error_message(err.error_code, str(err))) from None

        if not response or type(response) is not dict:
            raise ApiError("API returned unexpected response format for getPlayingContentInfo")

        return {
            "uri": coalesce_none_or_empty(response.get("uri")),
            "source": coalesce_none_or_empty(response.get("source")),
            "name": coalesce_none_or_empty(response.get("title"))
        }

    def set_play_content(self, uri):
        '''
        Activates the specified content on the target device.

        Args:
            uri (str): The URI at which the content can be accessed. Find the URI from the results of the
                :func:`get_content_list()` function.

        Raises:
            TypeError: One or more arguments is the incorrect type.
            ValueError: One or more arguments is invalid.
            ApiError: The request to the target device failed.
        '''

        self.bravia_client.initialize()

        if type(uri) is not str:
            raise TypeError("uri must be a string value")

        if not uri:
            raise ValueError("uri must be non-empty string")

        try:
            self.http_client.request(
                endpoint="avContent",
                method="setPlayContent",
                params={"uri": uri},
                version="1.0"
            )
        except HttpError as err:
            raise ApiError(get_error_message(err.error_code, str(err))) from None
