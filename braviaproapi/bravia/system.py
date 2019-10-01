from enum import Enum
from dateutil import parser as date_parser
from .errors import HttpError, ApiError, LanguageNotSupportedError, InternalError, ErrorCode, get_error_message
from .util import coalesce_none_or_empty


# Possible LED modes returned by API
class LedMode(Enum):
    '''
    Describes the mode of the LED indicator on the device.

    Attributes:
        UNKNOWN: The LED mode was not recognized.
        DEMO: The LED is in demo mode.
        AUTO_BRIGHTNESS: The LED adjusts its brightness based on the ambient light.
        DARK: The LED is dimmed.
        SIMPLE_RESPONSE: The LED lights only when responding to a command.
        OFF: The LED is disabled.
    '''
    UNKNOWN = 0
    DEMO = 1
    AUTO_BRIGHTNESS = 2
    DARK = 3
    SIMPLE_RESPONSE = 4
    OFF = 5


class PowerSavingMode(Enum):
    '''
    Describes the device's power saving mode.

    Attributes:
        UNKNOWN: The power saving mode was not recognized.
        OFF: Power saving is disabled.
        LOW: Power saving mode is set to low.
        HIGH: Power saving mode is set to high.
        PICTURE_OFF: The display is disabled.
    '''

    UNKNOWN = 0,
    OFF = 1,
    LOW = 2,
    HIGH = 3,
    PICTURE_OFF = 4


class System(object):
    '''
    Provides functionality for configuring the target device.

    Args:
        bravia_client: The parent :class:`BraviaClient` instance.
        http_client: The :class:`Http` instance associated with the parent client.
    '''

    def __init__(self, bravia_client, http_client):
        self.bravia_client = bravia_client
        self.http_client = http_client

    def power_on(self):
        '''
        Wakes up the target device.

        Raises:
            ApiError: The request to the target device failed.
        '''
        self.bravia_client.initialize()

        self.set_power_status(True)

    def power_off(self):
        '''
        Puts the target device into standby.

        Raises:
            ApiError: The request to the target device failed.
        '''
        self.bravia_client.initialize()

        self.set_power_status(False)

    def set_power_status(self, power_state):
        '''
        Wakes or sleeps the target device.

        Args:
            power_state (bool): True to wake, False to sleep.

        Raises:
            TypeError: One or more arguments is the incorrect type.
            ApiError: The request to the target device failed.
        '''
        self.bravia_client.initialize()

        if type(power_state) is not bool:
            raise TypeError("power_state must be a boolean type")

        try:
            self.http_client.request(
                endpoint="system",
                method="setPowerStatus",
                params={"status": power_state},
                version="1.0"
            )
        except HttpError as err:
            raise ApiError(get_error_message(err.error_code, str(err))) from None

    def get_power_status(self):
        '''
        Returns the current power state of the target device:

        Raises:
            ApiError: The request to the target device failed.

        Returns:
            bool: True if device is awake, False if the device is in standby.
        '''

        self.bravia_client.initialize()

        try:
            response = self.http_client.request(endpoint="system", method="getPowerStatus", version="1.0")
        except HttpError as err:
            raise ApiError(get_error_message(err.error_code, str(err))) from None

        if response["status"] == "standby":
            return False

        if response["status"] == "active":
            return True

        raise ApiError("Unexpected getPowerStatus response '{0}'".format(response["status"]))

    def get_current_time(self):
        '''
        Gets the current system time, if set.

        Raises:
            ApiError: The request to the target device failed.

        Returns:
            DateTime or None: The current system time. If the time is not set, returns `None`.
        '''

        self.bravia_client.initialize()

        try:
            response = self.http_client.request(endpoint="system", method="getCurrentTime", version="1.1")
            date = date_parser.parse(response["dateTime"])
            return date

        except HttpError as err:
            # Illegal state indicates that the system clock is not set, so there is no time to return.
            if (err.error_code == ErrorCode.ILLEGAL_STATE.value):
                return None
            else:
                raise ApiError(get_error_message(err.error_code, str(err))) from None

    def get_interface_information(self):
        '''
        Returns information about the server on the target device. This is used internally to check the current API
        version.

        Raises:
            ApiError: The request to the target device failed.

        Returns:
            dict: A dict containing the following keys:

            * product_category (`str or None`): The device's category name.
            * model_name (`str or None`): The model of the device.
            * product_name (`str or None`): The product name of the device;
            * server_name (`str or None`): The name of the server, if the device supports multiple.
            * interface_version (`str or None`): The `semver <https://semver.org/>`_ API version.
        '''

        # Do not initialize the client in this method, as it is used to determine API version during initialization.

        try:
            response = self.http_client.request(endpoint="system", method="getInterfaceInformation", version="1.0")
        except HttpError as err:
            raise ApiError(get_error_message(err.error_code, str(err))) from None

        interface_info = {
            "product_category": coalesce_none_or_empty(response.get("productCategory")),
            "product_name": coalesce_none_or_empty(response.get("productName")),
            "model_name": coalesce_none_or_empty(response.get("modelName")),
            "server_name": coalesce_none_or_empty(response.get("serverName")),
            "interface_version": coalesce_none_or_empty(response.get("interfaceVersion"))
        }

        return interface_info

    def get_led_status(self):
        '''
        Returns the current mode of the device's LED and whether it is enabled.

        Raises:
            ApiError: The request to the target device failed.

        Returns:
            dict or None: A dict containing the following keys, or `None` if the LED mode cannot be determined.

            * status (`bool or None`): Whether the LED is enabled or not.
            * mode (:class:`LedMode`): Which LED mode the target device is currently using.
        '''

        self.bravia_client.initialize()

        try:
            response = self.http_client.request(endpoint="system", method="getLEDIndicatorStatus", version="1.0")
        except HttpError as err:
            if err.error_code == ErrorCode.ILLEGAL_STATE.value:
                return None
            else:
                raise ApiError(get_error_message(err.error_code, str(err))) from None

        # API may return None for LED status if it is unknown
        led_status = None
        if "status" in response:
            if response["status"] == "true":
                led_status = True
            elif response["status"] == "false":
                led_status = False

        led_mode = None
        if "mode" in response:
            valid_modes = {
                "Demo": LedMode.DEMO,
                "AutoBrightnessAdjust": LedMode.AUTO_BRIGHTNESS,
                "Dark": LedMode.DARK,
                "SimpleResponse": LedMode.SIMPLE_RESPONSE,
                "Off": LedMode.OFF
            }
            led_mode = valid_modes.get(response.get("mode"), LedMode.UNKNOWN)

            if led_mode == LedMode.UNKNOWN:
                raise ApiError("API returned unexpected LED mode '{0}'".format(response.get("mode")))

        return {
            "status": led_status,
            "mode": led_mode
        }

    def get_network_settings(self, interface=None):
        '''
        Returns informaton about the target device's network configuration.

        Args:
            interface (str, optional): Defaults to `None` (all interfaces). The interface to get information about.

        Raises:
            ApiError: The request to the target device failed.

        Returns:
            list(dict) or None: A list of dicts containing the following keys. If an interface is specified and\
                                not found, returns `None`.

            * name (`str or None`): The name of the interface.
            * mac (`str or None`): The MAC address of the interface.
            * ip_v4 (`str or None`): The IPv4 address of the interface, if available.
            * ip_v6 (`str or None`): The IPv6 address of the interface, if available.
            * netmask (`str or None`): The network mask for the interface.
            * gateway (`str or None`): The configured gateway address for the interface.
            * dns_servers (`list(str)`): A list of DNS servers configured on the interface.
        '''

        self.bravia_client.initialize()

        request_interface = interface or ""

        if type(request_interface) is not str:
            raise TypeError("interface argument must be a string")

        try:
            response = self.http_client.request(
                endpoint="system",
                method="getNetworkSettings",
                version="1.0",
                params={"netif": request_interface}
            )
        except HttpError as err:
            # An illegal argument error indicates the requested interface does not exist. Gracefully handle this.
            if err.error_code == ErrorCode.ILLEGAL_ARGUMENT.value:
                return None
            else:
                raise ApiError(get_error_message(err.error_code, str(err))) from None

        if type(response) is not list:
            raise ApiError("API returned unexpected response format for getNetworkSettings")

        network_interfaces = []
        for iface in response:
            dns = iface.get("dns")

            iface_info = {
                "name": coalesce_none_or_empty(iface.get("netif")),
                "mac": coalesce_none_or_empty(iface.get("hwAddr")),
                "ip_v4": coalesce_none_or_empty(iface.get("ipAddrV4")),
                "ip_v6": coalesce_none_or_empty(iface.get("ipAddrV6")),
                "netmask": coalesce_none_or_empty(iface.get("netmask")),
                "gateway": coalesce_none_or_empty(iface.get("gateway")),
                "dns_servers": dns if type(dns) is list and len(dns) > 0 else []
            }
            network_interfaces.append(iface_info)

        # If a specific interface was requested, pull it out of the list
        if interface is not None:
            return network_interfaces[0]
        else:
            return network_interfaces

    def get_power_saving_mode(self):
        '''
        Returns the current power saving mode of the device.

        Raises:
            ApiError: The request to the target device failed.

        Returns:
            PowerSavingMode: The current power saving mode.
        '''

        self.bravia_client.initialize()

        try:
            response = self.http_client.request(endpoint="system", method="getPowerSavingMode", version="1.0")
        except HttpError as err:
            raise ApiError(get_error_message(err.error_code, str(err))) from None

        saving_mode = None
        if "mode" in response:
            valid_modes = {
                "off": PowerSavingMode.OFF,
                "low": PowerSavingMode.LOW,
                "high": PowerSavingMode.HIGH,
                "pictureOff": PowerSavingMode.PICTURE_OFF
            }
            saving_mode = valid_modes.get(response.get("mode"), PowerSavingMode.UNKNOWN)

            if saving_mode == PowerSavingMode.UNKNOWN:
                raise ApiError("API returned unexpected power saving mode '{0}'".format(response.get("mode")))

        return saving_mode

    def get_remote_control_info(self):
        '''
        Returns a list of IRCC remote codes supported by the target device.

        Raises:
            ApiError: The request to the target device failed.

        Returns:
            dict: A mapping of remote control button name (`str`) to IRCC code (`str`).
        '''

        self.bravia_client.initialize()

        try:
            response = self.http_client.request(endpoint="system", method="getRemoteControllerInfo", version="1.0")
        except HttpError as err:
            raise ApiError(get_error_message(err.error_code, str(err))) from None

        if len(response) != 2:
            raise ApiError("API returned unexpected format for remote control information.")

        button_codes = {}

        for button in response[1]:
            button_codes[button["name"]] = button["value"]

        return button_codes

    def get_remote_access_status(self):
        '''
        Returns whether remote access is enabled on the target device.

        Raises:
            ApiError: The request to the target device failed.

        Returns:
            bool: True if remote access is enabled, False otherwise.
        '''

        self.bravia_client.initialize()

        try:
            response = self.http_client.request(
                endpoint="system",
                method="getRemoteDeviceSettings",
                params={"target": "accessPermission"},
                version="1.0"
            )
        except HttpError as err:
            raise ApiError(get_error_message(err.error_code, str(err))) from None

        if type(response) is not list or len(response) != 1:
            raise ApiError("API returned unexpected getRemoteDeviceSettings response format")

        if response[0].get("currentValue") == "on":
            return True
        elif response[0].get("currentValue") == "off":
            return False
        else:
            raise ApiError(
                "API returned unexpected getRemoteDeviceSettings response '{0}'".format(response)
            )

    def get_system_information(self):
        '''
        Returns information about the target device.

        Raises:
            ApiError: The request to the target device failed.

        Returns:
            dict: A dict containing the following keys:

            * product (`str or None`): The product name.
            * language (`str or None`): The configured UI language.
            * model (`str or None`): The device model.
            * serial (`str or None`): The serial number of the device.
            * mac (`str or None`): The device's MAC address.
            * name (`str or None`): The name of the device.
            * generation (`str or None`): The `semver <https://semver.org/>`_ representation of the device's generation.
        '''

        self.bravia_client.initialize()

        try:
            response = self.http_client.request(endpoint="system", method="getSystemInformation", version="1.0")
        except HttpError as err:
            raise ApiError(get_error_message(err.error_code, str(err))) from None

        sys_info = {
            "product": coalesce_none_or_empty(response.get("product")),
            "language": coalesce_none_or_empty(response.get("language")),
            "model": coalesce_none_or_empty(response.get("model")),
            "serial": coalesce_none_or_empty(response.get("serial")),
            "mac": coalesce_none_or_empty(response.get("macAddr")),
            "name": coalesce_none_or_empty(response.get("name")),
            "generation": coalesce_none_or_empty(response.get("generation"))
        }

        return sys_info

    def get_wake_on_lan_mac(self):
        '''
        Returns the Wake-on-LAN (WOL) MAC address for the target device, if available.

        Raises:
            ApiError: The request to the target device failed.

        Returns:
            str or None: String MAC address of the device (format `00:00:00:00:00:00`), or None if Wake-on-LAN is\
                         not available.
        '''

        self.bravia_client.initialize()

        try:
            response = self.http_client.request(endpoint="system", method="getSystemSupportedFunction", version="1.0")
        except HttpError as err:
            raise ApiError(get_error_message(err.error_code, str(err))) from None

        if type(response) is not list:
            raise ApiError("API returned unexpected getSystemSupportedFunction response format")

        for entry in response:
            if entry["option"] == "WOL":
                return entry["value"]

        return None

    def get_wake_on_lan_status(self):
        '''
        Returns whether the Wake-on-LAN (WOL) function of the target device is enabled.

        Raises:
            ApiError: The request to the target device failed.

        Returns:
            bool: True if Wake-on-LAN is enabled, False if not.
        '''

        self.bravia_client.initialize()

        try:
            response = self.http_client.request(endpoint="system", method="getWolMode", version="1.0")
        except HttpError as err:
            raise ApiError(get_error_message(err.error_code, str(err))) from None

        enabled = response.get("enabled")
        if enabled is None or type(enabled) is not bool:
            raise ApiError("API returned unexpected getWolMode response format")

        return enabled

    def request_reboot(self):
        '''
        Reboots the target device.

        Raises:
            ApiError: The request to the target device failed.
        '''

        self.bravia_client.initialize()

        try:
            self.http_client.request(endpoint="system", method="requestReboot", version="1.0")
        except HttpError as err:
            raise ApiError(get_error_message(err.error_code, str(err))) from None

    def set_led_status(self, mode):
        '''
        Sets the LED mode of the target device.

        Args:
            mode (LedMode): The LED mode to set. May not be `LedMode.UNKNOWN`.

        Raises:
            TypeError: One or more arguments is the incorrect type.
            ValueError: One or more arguments is invalid.
            ApiError: The request to the target device failed.
            InternalError: An internal error occurred.
        '''
        self.bravia_client.initialize()

        if type(mode) is not LedMode:
            raise TypeError("mode must be an LedMode enum value")

        if mode == LedMode.UNKNOWN:
            raise ValueError("mode cannot be LedMode.UNKNOWN")

        modes = {
            LedMode.AUTO_BRIGHTNESS: "AutoBrightnessAdjust",
            LedMode.DARK: "Dark",
            LedMode.SIMPLE_RESPONSE: "SimpleResponse",
            LedMode.DEMO: "Demo",
            LedMode.OFF: "Off"
        }
        sent_mode = modes.get(mode, LedMode.UNKNOWN)

        if sent_mode == LedMode.UNKNOWN:
            raise InternalError("Internal error: unsupported LedMode selected")

        params = {
            "mode": sent_mode
        }

        try:
            self.http_client.request(endpoint="system", method="setLEDIndicatorStatus", params=params, version="1.1")
        except HttpError as err:
            raise ApiError(get_error_message(err.error_code, str(err))) from None

    def set_language(self, language):
        '''
        Sets the UI language of the target device. Language availabilit depends on the device's region settings.

        Args:
            language (str): The `ISO-639-3 <https://iso639-3.sil.org/code_tables/639/data>`_ code for the\
                desired language.

        Raises:
            TypeError: One or more arguments is the incorrect type.
            ApiError: The request to the target device failed.
            LanguageNotSupportedError: The specified language is not supported by the device.
        '''

        self.bravia_client.initialize()

        if type(language) is not str:
            raise TypeError("language must be a string value")

        try:
            self.http_client.request(
                endpoint="system",
                method="setLanguage",
                params={"language": language},
                version="1.0"
            )
        except HttpError as err:
            if err.error_code == ErrorCode.ILLEGAL_ARGUMENT.value:
                raise LanguageNotSupportedError()
            else:
                raise ApiError(get_error_message(err.error_code, str(err))) from None

    def set_power_saving_mode(self, mode):
        '''
        Sets the specified power saving mode on the target device.

        Args:
            mode (PowerSavingMode): The power saving mode to set. May not be `PowerSavingMode.UNKNOWN`.

        Raises:
            TypeError: One or more arguments is the incorrect type.
            ValueError: One or more arguments is invalid.
            ApiError: The request to the target device failed.
            InternalError: An internal error occurred.
        '''
        self.bravia_client.initialize()

        if type(mode) is not PowerSavingMode:
            raise TypeError("mode must be a PowerSavingMode enum value")

        if mode == PowerSavingMode.UNKNOWN:
            raise ValueError("mode cannot be PowerSavingMode.UNKNOWN")

        modes = {
            PowerSavingMode.OFF: "off",
            PowerSavingMode.LOW: "low",
            PowerSavingMode.HIGH: "high",
            PowerSavingMode.PICTURE_OFF: "pictureOff"
        }
        sent_mode = modes.get(mode, PowerSavingMode.UNKNOWN)

        if sent_mode == PowerSavingMode.UNKNOWN:
            raise InternalError("Internal error: unsupported PowerSavingMode selected")

        try:
            self.http_client.request(
                endpoint="system",
                method="setPowerSavingMode",
                params={"mode": sent_mode},
                version="1.0"
            )
        except HttpError as err:
            raise ApiError(get_error_message(err.error_code, str(err))) from None

    def set_wake_on_lan_status(self, enabled):
        '''
        Enables or disables Wake-on-LAN (WOL) on the target device.

        Args:
            enabled (bool): Whether to enable Wake-on-LAN.

        Raises:
            TypeError: One or more arguments is the incorrect type.
            ApiError: The request to the target device failed.
        '''

        self.bravia_client.initialize()

        if type(enabled) is not bool:
            raise TypeError("enabled must be a boolean value")

        try:
            self.http_client.request(
                endpoint="system",
                method="setWolMode",
                params={"enabled": enabled},
                version="1.0"
            )
        except HttpError as err:
            raise ApiError(get_error_message(err.error_code, str(err))) from None
