class BraviaApiError(Exception):
    pass


class HttpError(Exception):
    def __init__(self, message, error_code=None):
        self.error_code = error_code
        pass
