import re
from enum import Enum
from .errors import HttpError, ApiError, InternalError, ErrorCode, get_error_message, \
    TargetNotSupportedError, VolumeOutOfRangeError


class AudioOutput(Enum):
    '''
    Describes the audio output device used by the target device.

    Attributes:
        UNKNOWN: The audio output was not recognized.
        SPEAKER: An external speaker.
        SPEAKER_HDMI: An external HDMI-connected speaker.
        HDMI: HDMI audio output.
        AUDIO_SYSTEM: Internal speakers.
    '''
    UNKNOWN = 0
    SPEAKER = 1
    SPEAKER_HDMI = 2
    HDMI = 3
    AUDIO_SYSTEM = 4


class TvPosition(Enum):
    '''
    Describes the mounting position of the device.

    Attributes:
        UNKNOWN: The TV position was not recognized.
        TABLE_TOP: The TV is standing on a table.
        WALL_MOUNT: The TV is mounted on a wall.
    '''
    UNKNOWN = 0
    TABLE_TOP = 1
    WALL_MOUNT = 2


class SubwooferPhase(Enum):
    '''
    Describes the phase polarity setting of the wireless subwoofer.

    Attributes:
        UNKNOWN: The subwoofer phase was not recognized.
        NORMAL: The subwoofer is using normal polarity.
        REVERSE: The subwoofer is using reverse polarity.
    '''
    UNKNOWN = 0
    NORMAL = 1
    REVERSE = 2


class VolumeDevice(Enum):
    '''
    Describes the output device that the volume level is applied to.

    Attributes:
        UNKNOWN: The volume device was not recognized.
        SPEAKERS: The speaker output.
        HEADPHONES: The headphone output.
    '''
    UNKNOWN = 0
    SPEAKERS = 1
    HEADPHONES = 2


class SpeakerSetting(Enum):
    '''
    Describes available settings relating to audio.

    Attributes:
        UNKNOWN: The SpeakerSetting was not recognized.
        TV_POSITION: The mounting position of the device.
        SUBWOOFER_LEVEL: The volume level of the wireless subwoofer.
        SUBWOOFER_FREQUENCY: The frequency setting of the wireless subwoofer.
        SUBWOOFER_PHASE: The phase polarity of the wireless subwoofer.
        SUBWOOFER_POWER: Whether the wireless subwoofer is powered on or not.
    '''
    UNKNOWN = 0
    TV_POSITION = 1
    SUBWOOFER_LEVEL = 2
    SUBWOOFER_FREQUENCY = 3
    SUBWOOFER_PHASE = 4
    SUBWOOFER_POWER = 5


class Audio(object):
    '''
    Provides functionality for controlling audio on the target device.

    Args:
        bravia_client: The parent :class:`BraviaClient` instance.
        http_client: The :class:`Http` instance associated with the parent client.
    '''

    def __init__(self, bravia_client, http_client):
        self.bravia_client = bravia_client
        self.http_client = http_client

    def get_output_device(self):
        '''
        Returns the current audio output device on the target device.

        Raises:
            ApiError: The request to the target device failed.

        Returns:
            AudioOutput: The current output device.
        '''

        self.bravia_client.initialize()

        try:
            response = self.http_client.request(
                endpoint="audio",
                method="getSoundSettings",
                params={"target": "outputTerminal"},
                version="1.1"
            )
        except HttpError as err:
            if err.error_code == ErrorCode.ILLEGAL_ARGUMENT.value:
                # The requested target does not exist, but that's not necessarily a fatal error
                return None
            else:
                raise ApiError(get_error_message(err.error_code, str(err))) from None

        if type(response) is not list or len(response) > 1:
            raise ApiError("API returned unexpected response format for getSoundSettings")

        output_terminal = response[0]

        output_modes = {
            "speaker": AudioOutput.SPEAKER,
            "speaker_hdmi": AudioOutput.SPEAKER_HDMI,
            "hdmi": AudioOutput.HDMI,
            "audioSystem": AudioOutput.AUDIO_SYSTEM
        }
        current_output = output_modes.get(output_terminal.get("currentValue"), AudioOutput.UNKNOWN)

        if current_output == AudioOutput.UNKNOWN:
            raise ApiError(
                "API returned unexpected audio output '{0}'".format(output_terminal.get("currentValue"))
            )

        return {
            "output": current_output
        }

    def get_speaker_settings(self):
        '''
        Returns the current audio settings for the target device.

        Raises:
            ApiError: The request to the target device failed.

        Returns:
            dict: A dict with the following :class:`SpeakerSetting` keys. Each key's value may be `None` if the target\
            device does not provide that setting.

            * `SpeakerSetting.TV_POSITION` (:class:`TvPosition`): The physical location of the device.
            * `SpeakerSetting.SUBWOOFER_LEVEL` (`int`): The configured volume of the subwoofer.
            * `SpeakerSetting.SUBWOOFER_PHASE` (:class:`SubwooferPhase`): The phase setting of the subwoofer.
            * `SpeakerSetting.SUBWOOFER_FREQUENCY` (`int`): The confiugred frequency at which the subwoofer activates.
            * `SpeakerSetting.SUBWOOFER_POWER` (`bool`): whether the subwoofer is powered on or not.
        '''

        self.bravia_client.initialize()

        try:
            response = self.http_client.request(
                endpoint="audio",
                method="getSpeakerSettings",
                params={"target": ""},
                version="1.0"
            )
        except HttpError as err:
            raise ApiError(get_error_message(err.error_code, str(err))) from None

        if type(response) is not list:
            raise ApiError("API returned unexpected response format for getSoundSettings.")

        settings = {
            SpeakerSetting.TV_POSITION: None,
            SpeakerSetting.SUBWOOFER_LEVEL: None,
            SpeakerSetting.SUBWOOFER_FREQUENCY: None,
            SpeakerSetting.SUBWOOFER_PHASE: None,
            SpeakerSetting.SUBWOOFER_POWER: None
        }

        valid_positions = {
            "tableTop": TvPosition.TABLE_TOP,
            "wallMount": TvPosition.WALL_MOUNT
        }

        valid_sub_phases = {
            "normal": SubwooferPhase.NORMAL,
            "reverse": SubwooferPhase.REVERSE
        }

        for setting in response:
            target = setting.get("target")

            if target == "tvPosition":
                position = valid_positions.get(setting.get("currentValue"), TvPosition.UNKNOWN)
                if position == TvPosition.UNKNOWN:
                    raise ApiError(
                        "API returned unexpected TV position '{0}'".format(setting.get("currentValue"))
                    )
                settings[SpeakerSetting.TV_POSITION] = position

            elif target == "subwooferLevel":
                settings[SpeakerSetting.SUBWOOFER_LEVEL] = setting.get("currentValue")

            elif target == "subwooferFreq":
                settings[SpeakerSetting.SUBWOOFER_FREQUENCY] = setting.get("currentValue")

            elif target == "subwooferPhase":
                phase = valid_sub_phases.get(setting.get("currentValue"), SubwooferPhase.UNKNOWN)
                if phase == SubwooferPhase.UNKNOWN:
                    raise ApiError(
                        "API returned unexpected subwoofer phase '{0}'".format(setting.get("currentValue"))
                    )
                settings[SpeakerSetting.SUBWOOFER_PHASE] = phase

            elif target == "subwooferPower":
                settings[SpeakerSetting.SUBWOOFER_POWER] = True if setting.get("currentValue") == "on" else False

            # Skip settings that are unrecognized
            else:
                continue

        return settings

    def get_volume_information(self):
        '''
        Returns the current volume information of each audio output device on the target device.

        Raises:
            ApiError: The request to the target device failed.

        Returns:
            list(dict): A list of dicts containing the following properties:

            * min_volume (`int`): The minimum volume setting for the audio device.
            * max_volume (`int`): The maximum volume setting for the audio device.
            * muted (`bool`): whether the audio device is muted.
            * type (:class:`VolumeDevice`): The audio device represented by this entry.
            * volume (`int`): The current volume of the audio device.
        '''

        self.bravia_client.initialize()

        try:
            response = self.http_client.request(endpoint="audio", method="getVolumeInformation", version="1.0")
        except HttpError as err:
            raise ApiError(get_error_message(err.error_code, str(err))) from None

        if type(response) is not list:
            raise ApiError("API returned unexpected response format for getVolumeInformation.")

        valid_devices = {
            "speaker": VolumeDevice.SPEAKERS,
            "headphone": VolumeDevice.HEADPHONES
        }

        devices = []
        for this_device in response:
            device_type = valid_devices.get(this_device.get("target"))

            # Ignore unexpected device types
            if device_type is None:
                continue

            device_info = {
                "type": device_type,
                "volume": this_device.get("volume"),
                "muted": True if this_device.get("mute") else False,
                "min_volume": this_device.get("minVolume"),
                "max_volume": this_device.get("maxVolume")
            }
            devices.append(device_info)

        return devices

    def mute(self):
        '''
        Mutes the current audio output device on the target device.

        Raises:
            ApiError: The request to the target device failed.
        '''

        self.set_mute(True)

    def unmute(self):
        '''
        Unmutes the current audio output device on the target device.

        Raises:
            ApiError: The request to the target device failed.
        '''

        self.set_mute(False)

    def set_mute(self, mute):
        '''
        Mutes or unmutes the current audio output device on the target device.

        Args:
            mute (bool): If True, mutes the device. Otherwise, unmutes the device.

        Raises:
            TypeError: One or more arguments is the incorrect type.
            ApiError: The request to the target device failed.
        '''

        self.bravia_client.initialize()

        if type(mute) is not bool:
            raise TypeError("mute must be a boolean value")

        try:
            self.http_client.request(
                endpoint="audio",
                method="setAudioMute",
                params={"status": mute},
                version="1.0"
            )
        except HttpError as err:
            raise ApiError(get_error_message(err.error_code, str(err))) from None

    def set_volume_level(self, volume, show_ui=True, device=None):
        '''
        Sets the volume level of the specified audio output device on the target device.

        Args:
            volume (int): The volume to set on the target device. Generally this is on a scale from 0 to 100, but\
                this may vary by device.
            show_ui (bool, optional): Defaults to True. Whether to display the volume UI on the target device when\
                changing volume.
            device (VolumeDevice, optional): Defaults to `None`. Specifies which audio device to change the volume of.\
                 If not specified, affects all audio devices. May not be `VolumeDevice.UNKNOWN`.

        Raises:
            TypeError: One or more arguments is the incorrect type.
            ValueError: One or more arguments is invalid.
            ApiError: The request to the target device failed.
            VolumeOutOfRangeError: The specified volume is out of range for the target device.
            TargetNotSupportedError: The specified audio device is not supported by the target device.
            InternalError: An internal error occurred.
        '''
        if type(volume) is not int:
            raise TypeError("volume must be an integer value")

        self.__set_volume(volume, show_ui, device)

    def increase_volume(self, increase_by=1, show_ui=True, device=None):
        '''
        Increases volume level of the specified audio output device on the target device.

        Args:
            increase_by (int, optional): Defaults to 1. How many units to increase the volume on the target device.
            show_ui (bool, optional): Defaults to True. Whether to display the volume UI on the target device when\
                changing volume.
            device (VolumeDevice, optional): Defaults to `None`. Specifies which audio device to change the volume of.\
                If not specified, affects all audio devices. May not be `VolumeDevice.UNKNOWN`.

        Raises:
            TypeError: One or more arguments is the incorrect type.
            ValueError: One or more arguments is invalid.
            ApiError: The request to the target device failed.
            VolumeOutOfRangeError: The specified volume is out of range for the target device.
            TargetNotSupportedError: The specified audio device is not supported by the target device.
            InternalError: An internal error occurred.
        '''
        if type(increase_by) is not int:
            raise TypeError("increase_by must be an integer value")

        self.__set_volume("+" + str(increase_by), show_ui, device)

    def decrease_volume(self, decrease_by=1, show_ui=True, device=None):
        '''
        Decreases volume level of the specified audio output device on the target device.

        Args:
            decrease_by (int, optional): Defaults to 1. How many units to decrease the volume on the target device.
            show_ui (bool, optional): Defaults to True. Whether to display the volume UI on the target device when\
                changing volume.
            device (VolumeDevice, optional): Defaults to `None`. Specifies which audio device to change the volume of.\
                If not specified, affects all audio devices. May not be `VolumeDevice.UNKNOWN`.

        Raises:
            TypeError: One or more arguments is the incorrect type.
            ValueError: One or more arguments is invalid.
            ApiError: The request to the target device failed.
            VolumeOutOfRangeError: The specified volume is out of range for the target device.
            TargetNotSupportedError: The specified audio device is not supported by the target device.
            InternalError: An internal error occurred.
        '''
        if type(decrease_by) is not int:
            raise TypeError("decrease_by must be an integer value")

        self.__set_volume("-" + str(decrease_by), show_ui, device)

    def __set_volume(self, volume, show_ui=True, device=None):
        self.bravia_client.initialize()

        if device is not None and type(device) is not VolumeDevice:
            raise TypeError("device must be a VolumeDevice enum type or None")

        if device == VolumeDevice.UNKNOWN:
            raise ValueError("device cannot be VolumeDevice.UNKNOWN")

        if type(volume) is not int and type(volume) is not str:
            raise TypeError("volume must be an int or string")

        if type(volume) is str:
            if re.match(r'^[+-]\d+$', volume) is None:
                raise ValueError("volume must be in the format 1, +1, or -1")

        if type(show_ui) is not bool:
            raise TypeError("show_ui must be a boolean value")

        if device is None:
            target = ""
        else:
            valid_requested_devices = {
                VolumeDevice.SPEAKERS: "speaker",
                VolumeDevice.HEADPHONES: "headphone"
            }
            target = valid_requested_devices.get(device)
            if target is None:
                raise InternalError("Internal error: Invalid VolumeDevice specified")

        try:
            self.http_client.request(
                endpoint="audio",
                method="setAudioVolume",
                params={
                    "target": target,
                    "volume": str(volume),
                    "ui": "on" if show_ui else "off"
                },
                version="1.2"
            )
        except HttpError as err:
            if err.error_code == ErrorCode.TARGET_NOT_SUPPORTED.value:
                raise TargetNotSupportedError(
                    "The target device does not support controlling volume of the specified output."
                )
            if err.error_code == ErrorCode.VOLUME_OUT_OF_RANGE.value:
                raise VolumeOutOfRangeError("The specified volume value is out of range for the target device.")
            else:
                raise ApiError(get_error_message(err.error_code, str(err))) from None

    def set_output_device(self, output_device):
        '''
        Sets which audio output device the target device should use.

        Args:
            output_device (AudioOutput): The output device to use. May not be `AudioOutput.UNKNOWN`.

        Raises:
            TypeError: One or more arguments is the incorrect type.
            ValueError: One or more arguments is invalid.
            ApiError: The request to the target device failed.
            InternalError: An internal error occurred.
        '''

        self.bravia_client.initialize()

        if type(output_device) is not AudioOutput:
            raise TypeError("output_device must be an AudioOutput enum type")

        if output_device == AudioOutput.UNKNOWN:
            raise ValueError("output_device cannot be AudioOutput.UNKNOWN")

        valid_outputs = {
            AudioOutput.SPEAKER: "speaker",
            AudioOutput.SPEAKER_HDMI: "speaker_hdmi",
            AudioOutput.HDMI: "hdmi",
            AudioOutput.AUDIO_SYSTEM: "audioSystem"
        }

        request_output = valid_outputs.get(output_device, AudioOutput.UNKNOWN)
        if request_output == AudioOutput.UNKNOWN:
            raise InternalError("Internal error: unsupported AudioOutput selected")

        try:
            self.http_client.request(
                endpoint="audio",
                method="setSoundSettings",
                params={"settings": [{"target": "outputTerminal", "value": request_output}]},
                version="1.1"
            )
        except HttpError as err:
            if err.error_code == ErrorCode.MULTIPLE_SETTINGS_FAILED.value:
                raise ApiError("Unable to set sound output device")
            else:
                raise ApiError(get_error_message(err.error_code, str(err))) from None

    def set_speaker_settings(self, settings):
        '''
        Configures the settings relating to speakers on the target device.

        Args:
            settings (dict): Must contain one or more of the following :class:`SpeakerSetting` keys.

                * `SpeakerSetting.TV_POSITION` (:class:`TvPosition`): The physical location of the device. May not\
                    be `TvPosition.UNKNOWN`.
                * `SpeakerSetting.SUBWOOFER_LEVEL` (`int`): The configured volume of the subwoofer. Generally a value\
                    between 0 and 24, but may vary by device.
                * `SpeakerSetting.SUBWOOFER_PHASE` (:class:`SubwooferPhase`): The phase setting of the subwoofer. May\
                    not be `SubwooferPhase.UNKNOWN`.
                * `SpeakerSetting.SUBWOOFER_FREQUENCY` (`int`): The confiugred frequency at which the subwoofer\
                    activates. Generally a value between 0 and 30, but may vary by device.
                * `SpeakerSetting.SUBWOOFER_POWER` (`bool`): whether the subwoofer is powered on or not.

        Raises:
            TypeError: One or more members of the dict is the incorrect type.
            ValueError: One or more members of the dict is invalid.
            ApiError: The request to the target device failed.
            InternalError: An internal error occurred.
        '''

        self.bravia_client.initialize()

        if type(settings) is not dict:
            raise TypeError("settings must be a dict type")

        valid_targets = {
            SpeakerSetting.TV_POSITION: "tvPosition",
            SpeakerSetting.SUBWOOFER_LEVEL: "subwooferLevel",
            SpeakerSetting.SUBWOOFER_FREQUENCY: "subwooferFreq",
            SpeakerSetting.SUBWOOFER_PHASE: "subwooferPhase",
            SpeakerSetting.SUBWOOFER_POWER: "subwooferPower"
        }

        settings_to_request = []

        if settings.get(SpeakerSetting.TV_POSITION) is not None:
            position = self.__get_selected_tv_position(settings.get(SpeakerSetting.TV_POSITION))
            settings_to_request.append({"target": valid_targets[SpeakerSetting.TV_POSITION], "value": position})

        if settings.get(SpeakerSetting.SUBWOOFER_LEVEL) is not None:
            level = self.__get_selected_sub_level(settings.get(SpeakerSetting.SUBWOOFER_LEVEL))
            settings_to_request.append({"target": valid_targets[SpeakerSetting.SUBWOOFER_LEVEL], "value": level})

        if settings.get(SpeakerSetting.SUBWOOFER_FREQUENCY) is not None:
            frequency = self.__get_selected_sub_freq(settings.get(SpeakerSetting.SUBWOOFER_FREQUENCY))
            settings_to_request.append({
                "target": valid_targets[SpeakerSetting.SUBWOOFER_FREQUENCY],
                "value": frequency
            })

        if settings.get(SpeakerSetting.SUBWOOFER_PHASE) is not None:
            phase = self.__get_selected_sub_phase(settings.get(SpeakerSetting.SUBWOOFER_PHASE))
            settings_to_request.append({"target": valid_targets[SpeakerSetting.SUBWOOFER_PHASE], "value": phase})

        if settings.get(SpeakerSetting.SUBWOOFER_POWER) is not None:
            power = self.__get_selected_sub_power(settings.get(SpeakerSetting.SUBWOOFER_POWER))
            settings_to_request.append({
                "target": valid_targets[SpeakerSetting.SUBWOOFER_POWER],
                "value": power
            })

        if len(settings_to_request) == 0:
            raise ValueError("No valid settings were specified")

        try:
            self.http_client.request(
                endpoint="audio",
                method="setSpeakerSettings",
                params={"settings": settings_to_request},
                version="1.0"
            )
        except HttpError as err:
            raise ApiError(get_error_message(err.error_code, str(err))) from None

    def __get_selected_tv_position(self, value):
        if type(value) is not TvPosition:
            raise TypeError(
                "Setting value for SpeakerSetting.TV_POSITION must be specified as a TvPosition enum type"
            )

        if value == TvPosition.UNKNOWN:
            raise ValueError("Setting value for SpeakerSetting.TV_POSITION cannot be TvPosition.UNKNOWN")

        valid_positions = {
            TvPosition.TABLE_TOP: "tableTop",
            TvPosition.WALL_MOUNT: "wallMount"
        }

        position = valid_positions.get(value, TvPosition.UNKNOWN)

        if position == TvPosition.UNKNOWN:
            raise InternalError("Internal error: unsupported TvPosition selected")

        return position

    def __get_selected_sub_level(self, value):
        if type(value) is not int:
            raise TypeError("Setting value for SpeakerSetting.SUBWOOFER_LEVEL must be an integer type")

        return str(value)

    def __get_selected_sub_freq(self, value):
        if type(value) is not int:
            raise TypeError("Setting value for SpeakerSetting.SUBWOOFER_FREQUENCY must be an integer type")

        return str(value)

    def __get_selected_sub_phase(self, value):
        if type(value) is not SubwooferPhase:
            raise TypeError(
                ("Setting value for SpeakerSetting.SUBWOOFER_PHASE must be specified as "
                    "a SubwooferPhase enum type")
            )

        if value == SubwooferPhase.UNKNOWN:
            raise ValueError(
                "Setting value for SpeakerSetting.SUBWOOFER_PHASE cannot be SubwooferPhase.UNKNOWN"
            )

        valid_phases = {
            SubwooferPhase.NORMAL: "normal",
            SubwooferPhase.REVERSE: "reverse"
        }

        phase = valid_phases.get(value, SubwooferPhase.UNKNOWN)

        if phase == SubwooferPhase.UNKNOWN:
            raise InternalError("Internal error: unsupported SubwooferPhase selected")

        return phase

    def __get_selected_sub_power(self, value):
        if type(value) is not bool:
            raise TypeError("Setting value for SpeakerSetting.SUBWOOFER_POWER must be a boolean type")

        return "on" if value else "off"
