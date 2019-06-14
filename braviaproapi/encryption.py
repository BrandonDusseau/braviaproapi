from .errors import HttpError, BraviaApiError


class ErrorCode(object):
    ERR_KEY_DOES_NOT_EXIST = 42400


class Encryption(object):
    def __init__(self, bravia_client, http_client):
        self.bravia_client = bravia_client
        self.http_client = http_client

    def get_public_key(self):
        self.bravia_client.initialize()

        try:
            response = self.http_client.request(
                endpoint="encryption",
                method="getPublicKey",
                version="1.0"
            )
        except HttpError as err:
            # If we do not have a public key, return None
            if err.error_code == ErrorCode.ERR_KEY_DOES_NOT_EXIST:
                return None
            else:
                raise err

        if "publicKey" not in response:
            raise BraviaApiError("API returned unexpected response format for getPublicKey")

        return response["publicKey"]
