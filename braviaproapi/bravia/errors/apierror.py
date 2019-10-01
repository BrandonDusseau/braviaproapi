class ApiError(Exception):
    '''
    An error occurred while making an API request.
    '''
    pass


class EncryptionError(ApiError):
    '''
    An error occurred while encrypting or decrypting a message.
    '''
    pass


class TargetNotSupportedError(ApiError):
    '''
    The specified target is not supported by the device.
    '''
    pass


class LanguageNotSupportedError(ApiError):
    '''
    The specified UI language is not supported by the device.
    '''
    pass


class VolumeOutOfRangeError(ApiError):
    '''
    The specified volume level is out of range.
    '''
    pass


class AppLaunchError(ApiError):
    '''
    The requested app could not be launched.
    '''
    pass


class NoFocusedTextFieldError(ApiError):
    '''
    There is no text field focused on the device.
    '''
    pass


class InvalidStateError(ApiError):
    '''
    The device is not in a state where it can accept the request.
    '''
    pass
