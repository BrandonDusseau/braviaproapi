from .bravia import Http, System, VideoScreen, Encryption, AppControl, Audio, Remote, AvContent
from .bravia.errors import ApiError, HttpError
from packaging import version


class BraviaClient(object):
    '''
    Provides the client for interacting with the Bravia API.

    Attributes:
        appcontrol (AppControl): Provides app control and information.
        audio (Audio): Provides audio control and information.
        avcontent (AvContent): Provides control for content displayed by the device.
        encryption (Encryption): Provides access to device encryption.
        http_client (Http): HTTP client for direct API communication with the device.
        remote (Remote): Provides remote control input and information relating to it.
        system (System): Provides system information and configuration functionality.
        videoscreen (VideoScreen): Provides control of the device's display.

    Args:
        host (str): The IP address or domain name belonging to the target device.
        passcode (str): The pre-shared key configured on the target device.
    '''
    __initialized = False

    def __init__(self, host, passcode):
        self.http_client = Http(host=host, psk=passcode)
        self.encryption = Encryption(bravia_client=self, http_client=self.http_client)
        self.system = System(bravia_client=self, http_client=self.http_client)
        self.videoscreen = VideoScreen(bravia_client=self, http_client=self.http_client)
        self.appcontrol = AppControl(bravia_client=self, http_client=self.http_client)
        self.audio = Audio(bravia_client=self, http_client=self.http_client)
        self.remote = Remote(bravia_client=self, http_client=self.http_client)
        self.avcontent = AvContent(bravia_client=self, http_client=self.http_client)

    def initialize(self):
        '''
        Initializes the API client by verifying connectivity and compatibility with the target device.

        Raises:
            ApiError: The request to the target device failed.
        '''
        if self.__initialized:
            return

        # Verify that the API version is compatible
        try:
            interface_info = self.system.get_interface_information()
        except HttpError as err:
            raise ApiError(
                "Unable to verify API version compatibility due to an API error: {0}".format(str(err))
            ) from None

        api_version = interface_info["interface_version"]
        if api_version is None:
            raise ApiError(
                "Unable to verify API version compatibility because the device did not indicate its API version."
            )

        if (
            version.parse(api_version) >= version.parse("4.0.0")
            or version.parse(api_version) < version.parse("3.0.0")
        ):
            raise ApiError("The target device is running an incompatible API version '{0}'".format(api_version))

        self.__initialized = True
