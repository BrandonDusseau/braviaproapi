from . import http
from enum import Enum
from dateutil import parser as date_parser
from .http import HttpError
from .util import coalesce_none_or_empty
from pprint import pprint


# Error code definitions
class ErrorCode(object):
    ERR_CLOCK_NOT_SET = 7
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
                "pictureOff": PowerSavingMode.PICTURE_OFF,
                "Off": LedMode.OFF
            }
            saving_mode = valid_modes.get(response["mode"], PowerSavingMode.UNKNOWN)

            if saving_mode == PowerSavingMode.UNKNOWN:
                raise ValueError("API returned unexpected power saving mode '{0}'".format(response["mode"]))

        return {
            "mode": saving_mode
        }
