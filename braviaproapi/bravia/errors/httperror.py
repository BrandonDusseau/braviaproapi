class HttpError(Exception):
    '''
    An error occurred while communicating with the API.

    Attributes:
        error_code (str or None): The error code returned by the API, if any.
    '''

    def __init__(self, message, error_code=None):
        self.error_code = error_code
        pass
