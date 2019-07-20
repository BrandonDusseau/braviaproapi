from enum import Enum


class ApiErrors(Enum):
    UNKNOWN = 0

    # HTTP
    HTTP_UNAUTHORIZED = 401
    HTTP_FORBIDDEN = 403
    HTTP_NOT_FOUND = 404
    HTTP_ENTITY_TOO_LARGE = 413
    HTTP_URI_TOO_LONG = 414
    HTTP_NOT_IMPLEMENTED = 501
    HTTP_SERVICE_UNAVAILABLE = 503

    # Common
    ANY = 1
    TIMEOUT = 2
    ILLEGAL_ARGUMENT = 3
    ILLEGAL_REQUEST = 5
    ILLEGAL_STATE = 7
    NO_SUCH_METHOD = 12
    UNSUPPORTED_VERSION = 14
    UNSUPPORTED_OPERATION = 15
    REQUEST_RETRY = 40000
    CLIENT_OVER_MAXIMUM = 40001
    ENCRYPTION_FAILED = 40002
    REQUEST_DUPLICATED = 40003
    MULTIPLE_SETTINGS_FAILED = 40004
    DISPLAY_OFF = 40005
    CONTACT_SUPPORT = 40006

    # System
    PASSWORD_EXPIRED = 40200
    AC_POWER_REQUIRED = 40201

    # VideoScreen
    SCREEN_CHANGE_IN_PROGRESS = 40600

    # Audio
    TARGET_NOT_SUPPORTED = 40800
    VOLUME_OUT_OF_RANGE = 40801

    # AvContent
    CONTENT_PROTECTED = 41000
    CONTENT_DOES_NOT_EXIST = 41001
    STORAGE_HAS_NO_CONTENT = 41002
    SOME_CONTENT_NOT_DELETED = 41003
    CHANNEL_FIXED_BY_USB_RECORDING = 41011
    CHANNEL_FIXED_BY_SCART_RECORDING = 41012
    CHAPTER_DOES_NOT_EXIST = 41013
    CHANNEL_CANNOT_BE_DETERMINED = 41014
    EMPTY_CHANNEL_LIST = 41015
    STORAGE_DOES_NOT_EXIST = 41020
    STORAGE_FULL = 41021
    CONTENT_ATTRIBUTE_SETTING_FAILED = 41022
    UNKNOWN_GROUP_ID = 41023
    CONTENT_NOT_SUPPORTED = 41024

    # AppControl
    ANOTHER_REQUEST_IN_PROGRESS = 41400
    FAILED_TO_LAUNCH = 41401
    REQUEST_IN_PROGRESS = 41402
    FAILED_TO_TERMINATE = 41403

    # Encryption
    KEY_DOES_NOT_EXIST = 42400


error_messages = {
    ApiErrors.UNKNOWN: "An unexpected error occurred",
    ApiErrors.HTTP_UNAUTHORIZED: "This application is not authorized to access the device API",
    ApiErrors.HTTP_FORBIDDEN: "The requested resource is forbidden",
    ApiErrors.HTTP_NOT_FOUND: "The requested resource was not found",
    ApiErrors.HTTP_ENTITY_TOO_LARGE: "The content of the request was too large",
    ApiErrors.HTTP_URI_TOO_LONG: "The requested URI was too long",
    ApiErrors.HTTP_NOT_IMPLEMENTED: "The requested resource is not implemented",
    ApiErrors.HTTP_SERVICE_UNAVAILABLE: "The device API reports that it is not available",
    ApiErrors.ANY: "A general error occurred",
    ApiErrors.TIMEOUT: "A timeout occurred on the device",
    ApiErrors.ILLEGAL_ARGUMENT: "One or more API parameters is invalid on this device",
    ApiErrors.ILLEGAL_REQUEST: "The API request is malformed, empty, or otherwise invalid",
    ApiErrors.ILLEGAL_STATE: "The device is not in the correct state to process this request",
    ApiErrors.NO_SUCH_METHOD: "The requested API resource is not available on this device",
    ApiErrors.UNSUPPORTED_VERSION: "The requested API resource version is not available on this device",
    ApiErrors.UNSUPPORTED_OPERATION: "The device cannot handle the request with the specified parameters",
    ApiErrors.REQUEST_RETRY: "A long polling timeout occurred",  # What is this?
    ApiErrors.CLIENT_OVER_MAXIMUM: "Too many long polling clients are currently connected",  # What is this?
    ApiErrors.ENCRYPTION_FAILED: "The device was unable to encrypt its response, possibly due to an invalid key",
    ApiErrors.REQUEST_DUPLICATED: "The previous request is still processing",
    ApiErrors.MULTIPLE_SETTINGS_FAILED: "One or more settings could not be applied (but some may have been)",
    ApiErrors.DISPLAY_OFF: "This request cannot be made while the device's display is off",
    ApiErrors.CONTACT_SUPPORT: "A general error occurred with message",
    ApiErrors.PASSWORD_EXPIRED: "The password has expired",
    ApiErrors.AC_POWER_REQUIRED: "The request cannot be processed because the device needs to be connected to AC power",
    ApiErrors.SCREEN_CHANGE_IN_PROGRESS: "The device is currently changing the screen",
    ApiErrors.TARGET_NOT_SUPPORTED: "The specified target is not supported or cannot be controlled",
    ApiErrors.VOLUME_OUT_OF_RANGE: "The specified volume level is out of range for the device",
    ApiErrors.CONTENT_PROTECTED: "The requested content is DRM protected and cannot be used",
    ApiErrors.CONTENT_DOES_NOT_EXIST: "The requested content does not exist",
    ApiErrors.STORAGE_HAS_NO_CONTENT: "The requested storage device contains no content",
    ApiErrors.SOME_CONTENT_NOT_DELETED: "Some content could not be deleted as requested",
    ApiErrors.CHANNEL_FIXED_BY_USB_RECORDING: ("The content cannot be changed because the channel is fixed by a "
                                               + "USB recording device"),
    ApiErrors.CHANNEL_FIXED_BY_SCART_RECORDING: ("The content cannot be changed because the channel is fixed by a "
                                                 + "SCART recording device"),
    ApiErrors.CHAPTER_DOES_NOT_EXIST: "The requested chapter does not exist",
    ApiErrors.CHANNEL_CANNOT_BE_DETERMINED: "The channel cannot be determined at this time",
    ApiErrors.EMPTY_CHANNEL_LIST: "The channel list is empty",
    ApiErrors.STORAGE_DOES_NOT_EXIST: "The storage device does not exist",
    ApiErrors.STORAGE_FULL: "The storage device is full",
    ApiErrors.CONTENT_ATTRIBUTE_SETTING_FAILED: "Setting an attribute on the content failed",
    ApiErrors.UNKNOWN_GROUP_ID: "The specified group ID is unknown",
    ApiErrors.CONTENT_NOT_SUPPORTED: "The specified content is not supported",
    ApiErrors.ANOTHER_REQUEST_IN_PROGRESS: "Another request is already in progress",
    ApiErrors.FAILED_TO_LAUNCH: "The specified app failed to launch",
    ApiErrors.REQUEST_IN_PROGRESS: "The requested was accepted but the app's launch may still be in progress",
    ApiErrors.FAILED_TO_TERMINATE: "One or more apps failed to terminate",
    ApiErrors.KEY_DOES_NOT_EXIST: "The device has not yet generated an encryption key"
}


def getErrorMessage(error_code, additional_message=None):
    if error_code is not None:
        try:
            known_error_code = ApiErrors(error_code)
        except TypeError:
            known_error_code = ApiErrors.UNKNOWN
    else:
        known_error_code = ApiErrors.UNKNOWN

    if additional_message is None:
        return error_messages.get(known_error_code)
    else:
        return "{0}: {1}".format(error_messages.get(known_error_code), additional_message)


class BraviaApiError(Exception):
    pass


class HttpError(Exception):
    def __init__(self, message, error_code=None):
        self.error_code = error_code
        pass


class BraviaAppLaunchAlreadyInProgressError(Exception):
    pass


class BraviaAppLaunchError(Exception):
    pass


class BraviaNoFocusedTextFieldError(Exception):
    pass
