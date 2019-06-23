import re
from enum import Enum
from .errors import HttpError, BraviaApiError


# Error code definitions
class ErrorCode(object):
    ILLEGAL_ARGUMENT = 3
    ILLEGAL_STATE = 7
    TARGET_NOT_SUPPORTED = 40800
    VOLUME_OUT_OF_RANGE = 40801
    MULTIPLE_SETTINGS_FAILED = 40004


class AudioOutput(Enum):
    UNKNOWN = 0
    SPEAKER = 1
    SPEAKER_HDMI = 2
    HDMI = 3
    AUDIO_SYSTEM = 4


class TvPosition(Enum):
    UNKNOWN = 0
    TABLE_TOP = 1
    WALL_MOUNT = 2


class SubwooferPhase(Enum):
    UNKNOWN = 0
    NORMAL = 1
    REVERSE = 2


class VolumeDevice(Enum):
    UNKNOWN = 0
    SPEAKERS = 1
    HEADPHONES = 2


class SpeakerSetting(Enum):
    UNKNOWN = 0
    TV_POSITION = 1
    SUBWOOFER_LEVEL = 2
    SUBWOOFER_FREQUENCY = 3
    SUBWOOFER_PHASE = 4
    SUBWOOFER_POWER = 5


class Audio(object):
    def __init__(self, bravia_client, http_client):
        self.bravia_client = bravia_client
        self.http_client = http_client

    def get_output_device(self):
        self.bravia_client.initialize()

        try:
            response = self.http_client.request(
                endpoint="audio",
                method="getSoundSettings",
                params={"target": "outputTerminal"},
                version="1.1"
            )
        except HttpError as err:
            if err.error_code == ErrorCode.ILLEGAL_ARGUMENT:
                # The requested target does not exist, but that's not necessarily a fatal error
                return None
            else:
                raise BraviaApiError("An unexpected error occurred: {0}".format(str(err)))

        if type(response) is not list or len(response) > 1:
            raise BraviaApiError("API returned unexpected response format for getSoundSettings")

        output_terminal = response[0]

        output_modes = {
            "speaker": AudioOutput.SPEAKER,
            "speaker_hdmi": AudioOutput.SPEAKER_HDMI,
            "hdmi": AudioOutput.HDMI,
            "audioSystem": AudioOutput.AUDIO_SYSTEM
        }
        current_output = output_modes.get(output_terminal.get("currentValue"), AudioOutput.UNKNOWN)

        if current_output == AudioOutput.UNKNOWN:
            raise BraviaApiError(
                "API returned unexpected audio output '{0}'".format(output_terminal.get("currentValue"))
            )

        return {
            "output": current_output
        }

    def get_speaker_settings(self):
        self.bravia_client.initialize()

        response = self.http_client.request(
            endpoint="audio",
            method="getSpeakerSettings",
            params={"target": ""},
            version="1.0"
        )

        if type(response) is not list:
            raise BraviaApiError("API returned unexpected response format for getSoundSettings.")

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
                    raise BraviaApiError(
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
                    raise BraviaApiError(
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
        self.bravia_client.initialize()

        response = self.http_client.request(endpoint="audio", method="getVolumeInformation", version="1.0")

        if type(response) is not list:
            raise BraviaApiError("API returned unexpected response format for getVolumeInformation.")

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
        self.set_mute(True)

    def unmute(self):
        self.set_mute(False)

    def set_mute(self, mute):
        self.bravia_client.initialize()

        if type(mute) is not bool:
            raise TypeError("mute must be a boolean value")

        self.http_client.request(
            endpoint="audio",
            method="setAudioMute",
            params={"status": mute},
            version="1.0"
        )

    def set_volume_level(self, volume, show_ui=True, device=None):
        if type(volume) is not int:
            raise TypeError("volume must be an integer value")

        self.__set_volume(volume, show_ui, device)

    def increase_volume(self, increase_by=1, show_ui=True, device=None):
        if type(increase_by) is not int:
            raise TypeError("increase_by must be an integer value")

        self.__set_volume("+" + str(increase_by), show_ui, device)

    def decrease_volume(self, decrease_by=1, show_ui=True, device=None):
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
                raise BraviaApiError("Internal error: Invalid VolumeDevice specified")

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
            if err.error_code == ErrorCode.TARGET_NOT_SUPPORTED:
                raise BraviaApiError("The target device does not support controlling volume of the specified output.")
            if err.error_code == ErrorCode.VOLUME_OUT_OF_RANGE:
                raise BraviaApiError("The specified volume value is out of range for the target device.")
            else:
                raise BraviaApiError("An unexpected error occurred: {0}".format(str(err)))

    def set_output_device(self, output_device):
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
            raise BraviaApiError("Internal error: unsupported AudioOutput selected")

        try:
            self.http_client.request(
                endpoint="audio",
                method="setSoundSettings",
                params={"settings": [{"target": "outputTerminal", "value": request_output}]},
                version="1.1"
            )
        except HttpError as err:
            if err.error_code == ErrorCode.MULTIPLE_SETTINGS_FAILED:
                raise BraviaApiError("Unable to set sound output device")
            else:
                raise BraviaApiError("An unexpected error occurred: {0}".format(str(err)))

    def set_speaker_settings(self, settings):
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
            if err.error_code == ErrorCode.MULTIPLE_SETTINGS_FAILED:
                raise BraviaApiError("One or more settings failed to apply, but some may have been successful.")
            else:
                raise BraviaApiError("An unexpected error occurred: {0}".format(str(err)))

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
            raise BraviaApiError("Internal error: unsupported TvPosition selected")

        return position

    def __get_selected_sub_level(self, value):
        if type(value) is not int:
            raise TypeError("Setting value for SpeakerSetting.SUBWOOFER_LEVEL must be an integer type")

        if value < 0 or value > 24:
            raise ValueError(
                "Setting value for SpeakerSetting.SUBWOOFER_LEVEL must be between 0 and 24, inclusive"
            )

        return str(value)

    def __get_selected_sub_freq(self, value):
        if type(value) is not int:
            raise TypeError("Setting value for SpeakerSetting.SUBWOOFER_FREQUENCY must be an integer type")

        if value < 0 or value > 30:
            raise ValueError(
                "Setting value for SpeakerSetting.SUBWOOFER_FREQUENCY must be between 0 and 30, inclusive"
            )

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
            raise BraviaApiError("Internal error: unsupported SubwooferPhase selected")

        return phase

    def __get_selected_sub_power(self, value):
        if type(value) is not bool:
            raise TypeError("Setting value for SpeakerSetting.SUBWOOFER_POWER must be a boolean type")

        return "on" if value else "off"
