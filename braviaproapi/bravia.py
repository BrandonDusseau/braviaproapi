from . import http, system, videoscreen, encryption
from .errors import BraviaApiError
from packaging import version


class Bravia(object):
    initialized = False

    def __init__(self, host, passcode):
        self.http_client = http.Http(host=host, psk=passcode)
        self.system = system.System(bravia_client=self, http_client=self.http_client)
        self.videoscreen = videoscreen.VideoScreen(bravia_client=self, http_client=self.http_client)
        self.encryption = encryption.Encryption(bravia_client=self, http_client=self.http_client)

    def initialize(self):
        if self.initialized:
            return

        # Verify that the API version is compatible
        try:
            interface_info = self.system.get_interface_information()
        except http.HttpError as err:
            raise BraviaApiError(
                "Unable to verify API version compatibility due to an API error: {0}".format(str(err))
            ) from None

        api_version = interface_info["interface_version"]
        if api_version is None:
            raise BraviaApiError(
                "Unable to verify API version compatibility because the device did not indicate its API version."
            )

        if (
            version.parse(api_version) >= version.parse("4.0.0")
            or version.parse(api_version) < version.parse("3.0.0")
        ):
            raise BraviaApiError("The target device is running an incompatible API version '{0}'".format(api_version))

        self.initialized = True
