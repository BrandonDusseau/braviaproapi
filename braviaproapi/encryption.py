from .errors import HttpError, BraviaApiError
from base64 import b64encode
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad
from M2Crypto import RSA, BIO
from pprint import pprint


class ErrorCode(object):
    ERR_KEY_DOES_NOT_EXIST = 42400


class Encryption(object):
    def __init__(self, bravia_client, http_client):
        self.bravia_client = bravia_client
        self.http_client = http_client
        self.common_key = self.generate_common_key()

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

    def generate_common_key(self):
        return get_random_bytes(16)

    def get_encrypted_common_key(self):
        pubkey_base64 = self.get_public_key()

        if pubkey_base64 is None:
            return None

        # public_key = RSA.import_key(b64decode(pubkey_base64))
        # cipher = PKCS1_v1_5.new(public_key)
        # encrypted_key = cipher.encrypt(self.common_key)
        x509_pubkey = "-----BEGIN PUBLIC KEY-----\n{0}\n-----END PUBLIC KEY-----".format(pubkey_base64)
        bio = BIO.MemoryBuffer(x509_pubkey.encode("utf-8"))
        public_key = RSA.load_pub_key_bio(bio)
        encrypted_key = public_key.public_encrypt(self.common_key, RSA.pkcs1_padding)

        return b64encode(encrypted_key).decode("utf-8")

    def encrypt(self, message):
        cipher = AES.new(self.common_key, AES.MODE_CBC)
        ciphertext = cipher.encrypt(pad(message.encode(), AES.block_size))

        pprint(ciphertext)

        return b64encode(ciphertext).decode("utf-8")
