from .errors import HttpError, BraviaApiError
from base64 import b64encode, b64decode
from Crypto.Cipher import AES, PKCS1_v1_5
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
from pprint import pprint


class ErrorCode(object):
    ERR_KEY_DOES_NOT_EXIST = 42400


class Encryption(object):
    def __init__(self, bravia_client, http_client):
        self.bravia_client = bravia_client
        self.http_client = http_client
        self.aes_common_key = get_random_bytes(16)
        self.aes_initialization_vector = get_random_bytes(AES.block_size)

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

    def get_rsa_encrypted_common_key(self):
        try:
            pubkey_base64 = self.get_public_key()
        except [BraviaApiError, HttpError]:
            return None

        if pubkey_base64 is None:
            return None

        # Sony's server requires the AES key's hex representation to be contatenated with the
        # initialization vector's hex representation before encryption.
        # This is undocumented.
        aes_key_to_encrypt = self.aes_common_key.hex() + ":" + self.aes_initialization_vector.hex()

        public_key = RSA.import_key(b64decode(pubkey_base64))
        cipher = PKCS1_v1_5.new(public_key)
        encrypted_key = cipher.encrypt(aes_key_to_encrypt.encode("utf-8"))

        return b64encode(encrypted_key).decode("utf-8")

    def aes_encrypt_b64(self, message):
        cipher = AES.new(self.aes_common_key, AES.MODE_CBC, self.aes_initialization_vector)
        ciphertext = cipher.encrypt(pad(message.encode("utf-8"), AES.block_size))

        return b64encode(ciphertext).decode("utf-8")

    def aes_decrypt_b64(self, message):
        decoded_message = b64decode(message)
        cipher = AES.new(self.aes_common_key, AES.MODE_CBC, self.aes_initialization_vector)
        decrypted_message = unpad(cipher.decrypt(decoded_message), AES.block_size)

        return decrypted_message.decode("utf-8")
