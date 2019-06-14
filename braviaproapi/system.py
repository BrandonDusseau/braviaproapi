from . import http
from enum import Enum
from dateutil import parser as date_parser
from .errors import HttpError, BraviaApiError
from .util import coalesce_none_or_empty
from pprint import pprint


# Error code definitions
class ErrorCode(object):
    ERR_CLOCK_NOT_SET = 7
    ILLEGAL_STATE = 7
    ILLEGAL_ARGUMENT = 3


# Possible LED modes returned by API
class LedMode(Enum):
    UNKNOWN = 0
    DEMO = 1
    AUTO_BRIGHTNESS = 2
    DARK = 3
    SIMPLE_RESPONSE = 4
    OFF = 5


class PowerSavingMode(Enum):
    UNKNOWN = 0,
    OFF = 1,
    LOW = 2,
    HIGH = 3,
    PICTURE_OFF = 4


class System(object):
    def __init__(self, bravia_client, http_client):
        self.bravia_client = bravia_client
        self.http_client = http_client

    def power_on(self):
        self.bravia_client.initialize()

        self.set_power_status(True)

    def power_off(self):
        self.bravia_client.initialize()

        self.set_power_status(False)

    def set_power_status(self, power_state):
        self.bravia_client.initialize()

        if (not isinstance(power_state, bool)):
            raise ValueError("power_state must be a boolean")

        self.http_client.request(
            endpoint="system",
            method="setPowerStatus",
            params={"status": power_state},
            version="1.0"
        )

    def get_power_status(self):
        self.bravia_client.initialize()

        response = self.http_client.request(endpoint="system", method="getPowerStatus", version="1.0")

        if response["status"] == "standby":
            return False

        if response["status"] == "active":
            return True

        raise ValueError("Unexpected getPowerStatus response '{0}'".format(response["status"]))

    def get_current_time(self):
        self.bravia_client.initialize()

        try:
            response = self.http_client.request(endpoint="system", method="getCurrentTime", version="1.1")
            date = date_parser.parse(response["dateTime"])
            return date

        except HttpError as err:
            if (err.error_code == ErrorCode.ERR_CLOCK_NOT_SET):
                return None
            else:
                raise err

    def get_interface_information(self):
        response = self.http_client.request(endpoint="system", method="getInterfaceInformation", version="1.0")

        interface_info = {
            "product_category": coalesce_none_or_empty(response.get("productCategory")),
            "product_name": coalesce_none_or_empty(response.get("productName")),
            "model_name": coalesce_none_or_empty(response.get("modelName")),
            "server_name": coalesce_none_or_empty(response.get("serverName")),
            "interface_version": coalesce_none_or_empty(response.get("interfaceVersion"))
        }

        return interface_info

    def get_led_status(self):
        self.bravia_client.initialize()

        response = self.http_client.request(endpoint="system", method="getLEDIndicatorStatus", version="1.0")

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
            led_mode = valid_modes.get(response["mode"], LedMode.UNKNOWN)

            if led_mode == LedMode.UNKNOWN:
                raise ValueError("API returned unexpected LED mode '{0}'".format(response["mode"]))

        return {
            "status": led_status,
            "mode": led_mode
        }

    def get_network_settings(self, interface=None):
        self.bravia_client.initialize()

        request_interface = interface or ""

        if not isinstance(request_interface, str):
            raise ValueError("interface argument must be a string")

        try:
            response = self.http_client.request(
                endpoint="system",
                method="getNetworkSettings",
                version="1.0",
                params={"netif": request_interface}
            )
        except HttpError as err:
            # An illegal argument error indicates the requested interface does not exist. Gracefully handle this.
            if (err.error_code == ErrorCode.ILLEGAL_ARGUMENT):
                return None
            else:
                raise err

        network_interfaces = []
        for iface in response:
            iface_info = {
                "name": coalesce_none_or_empty(iface.get("netif")),
                "mac": coalesce_none_or_empty(iface.get("hwAddr")),
                "ip_v4": coalesce_none_or_empty(iface.get("ipAddrV4")),
                "ip_v6": coalesce_none_or_empty(iface.get("ipAddrV6")),
                "netmask": coalesce_none_or_empty(iface.get("netmask")),
                "gateway": coalesce_none_or_empty(iface.get("gateway")),
                "dns_servers": coalesce_none_or_empty(iface.get("dns"))
            }
            network_interfaces.append(iface_info)

        # If a specific interface was requested, pull it out of the list
        if interface is not None:
            return network_interfaces[0]
        else:
            return network_interfaces

    def get_power_saving_mode(self):
        self.bravia_client.initialize()

        response = self.http_client.request(endpoint="system", method="getPowerSavingMode", version="1.0")

        saving_mode = None
        if "mode" in response:
            valid_modes = {
                "off": PowerSavingMode.OFF,
                "low": PowerSavingMode.LOW,
                "high": PowerSavingMode.HIGH,
                "pictureOff": PowerSavingMode.PICTURE_OFF
            }
            saving_mode = valid_modes.get(response["mode"], PowerSavingMode.UNKNOWN)

            if saving_mode == PowerSavingMode.UNKNOWN:
                raise ValueError("API returned unexpected power saving mode '{0}'".format(response["mode"]))

        return {
            "mode": saving_mode
        }

    def get_remote_control_info(self):
        self.bravia_client.initialize()

        response = self.http_client.request(endpoint="system", method="getRemoteControllerInfo", version="1.0")

        if len(response) != 2:
            raise ValueError("API returned unexpected format for remote control information.")

        button_codes = {}

        for button in response[1]:
            button_codes[button["name"]] = button["value"]

        return button_codes

    def get_remote_access_status(self):
        self.bravia_client.initialize()

        response = self.http_client.request(
            endpoint="system",
            method="getRemoteDeviceSettings",
            params={"target": "accessPermission"},
            version="1.0"
        )

        if len(response) != 1:
            raise ValueError("API returned unexpected getRemoteDeviceSettings response format")

        if response[0]["currentValue"] == "on":
            return True

        if response[0]["currentValue"] == "false":
            return False

        raise ValueError(
            "API returned unexpected getRemoteDeviceSettings response '{0}'".format(response["currentValue"])
        )

    def get_system_information(self):
        self.bravia_client.initialize()

        response = self.http_client.request(endpoint="system", method="getSystemInformation", version="1.0")

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

    def get_wake_on_lan_information(self):
        self.bravia_client.initialize()

        response = self.http_client.request(endpoint="system", method="getSystemSupportedFunction", version="1.0")

        if len(response) != 1:
            raise ValueError("API returned unexpected getSystemSupportedFunction response format")

        wol_info = response[0]
        if wol_info["option"] != "WOL":
            raise ValueError("API returned unexpected option name '{0}'".format(wol_info["option"]))

        return {
            "mac": wol_info["value"]
        }

    def get_wake_on_lan_status(self):
        self.bravia_client.initialize()

        response = self.http_client.request(endpoint="system", method="getWolMode", version="1.0")

        enabled = response.get("enabled")
        if enabled is None or type(enabled) is not bool:
            raise ValueError("API returned unexpected getWolMode response format")

        return enabled

    def request_reboot(self):
        self.bravia_client.initialize()
        self.http_client.request(endpoint="system", method="requestReboot", version="1.0")

    def set_led_status(self, mode, enabled=None):
        self.bravia_client.initialize()

        if enabled is not None and type(enabled) is not bool:
            raise TypeError("enabled must be a boolean value or None")

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
            raise ValueError("Internal error: unsupported LedMode selected")

        params = {
            "mode": sent_mode
        }

        # Some TVs will return an error if status is not supported, even if set to None.
        if enabled is not None:
            params["status"] = enabled

        try:
            self.http_client.request(endpoint="system", method="setLEDIndicatorStatus", params=params, version="1.1")
        except HttpError as err:
            if err.error_code == ErrorCode.ILLEGAL_STATE or err.error_code == ErrorCode.ILLEGAL_ARGUMENT:
                raise BraviaApiError("The target device does not support setting LED status.")
            else:
                raise err

    def set_language(self, language):
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
            if err.error_code == ErrorCode.ILLEGAL_ARGUMENT:
                raise BraviaApiError("The target device does not support the selected language.")
            else:
                raise err

    def set_power_saving_mode(self, mode):
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
            raise ValueError("Internal error: unsupported PowerSavingMode selected")

        self.http_client.request(
            endpoint="system",
            method="setPowerSavingMode",
            params={"mode": sent_mode},
            version="1.0"
        )

    def set_wake_on_lan_status(self, enabled):
        self.bravia_client.initialize()

        if type(enabled) is not bool:
            raise TypeError("enabled must be a boolean value")

        self.http_client.request(
            endpoint="system",
            method="setWolMode",
            params={"enabled": enabled},
            version="1.0"
        )
