from .errors import HttpError, ApiError, ErrorCode, get_error_message
from base64 import b64encode, b64decode
from Crypto.Cipher import AES, PKCS1_v1_5
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad


class Encryption(object):
    '''
    Provides functionality for encrypted communication with the target device.

    Args:
        bravia_client: The parent :class:`BraviaClient` instance.
        http_client: The :class:`Http` instance associated with the parent client.
    '''

    def __init__(self, bravia_client, http_client):
        self.bravia_client = bravia_client
        self.http_client = http_client
        self.aes_common_key = get_random_bytes(16)
        self.aes_initialization_vector = get_random_bytes(AES.block_size)

    def get_public_key(self):
        '''
        Gets the target device's public encryption key.

        Raises:
            ApiError: The request to the target device failed.

        Returns:
            str or None: The device's public key, base64-encoded. If the device does not have a public key, returns\
                         `None`.
        '''

        self.bravia_client.initialize()

        try:
            response = self.http_client.request(
                endpoint="encryption",
                method="getPublicKey",
                version="1.0"
            )
        except HttpError as err:
            # If we do not have a public key, return None
            if err.error_code == ErrorCode.KEY_DOES_NOT_EXIST.value:
                return None
            else:
                raise ApiError(get_error_message(err.error_code, str(err))) from None

        if "publicKey" not in response:
            raise ApiError("API returned unexpected response format for getPublicKey")

        return response["publicKey"]

    def get_rsa_encrypted_common_key(self):
        '''
        Returns a common key to be used in encrypted communication with the target device.

        This common key is generated when the Bravia client is initialized and used throghout the life of the
        application.

        Returns:
            str: An AES common key, encrypted with RSA, to be sent to the target device. If no encryption
                 capability is available on the target device, returns `None`.
        '''

        try:
            pubkey_base64 = self.get_public_key()
        except [ApiError, HttpError]:
            return None

        # get_public_key may return None
        if pubkey_base64 is None:
            return None

        # Sony's server requires the AES key's hex representation to be concatenated with the
        # initialization vector's hex representation before encryption.
        # This is undocumented.
        aes_key_to_encrypt = self.aes_common_key.hex() + ":" + self.aes_initialization_vector.hex()

        public_key = RSA.import_key(b64decode(pubkey_base64))
        cipher = PKCS1_v1_5.new(public_key)
        encrypted_key = cipher.encrypt(aes_key_to_encrypt.encode("utf-8"))

        return b64encode(encrypted_key).decode("utf-8")

    def aes_encrypt_b64(self, message):
        '''
        Encrypts AES messages to be sent to the target device.

        Args:
            message (str): The message to encrypt.

        Raises:
            TypeError: One or more arguments is the incorrect type.

        Returns:
            str: The encrypted string.
        '''

        if type(message) is not str:
            raise TypeError("message must be a str value")

        cipher = AES.new(self.aes_common_key, AES.MODE_CBC, self.aes_initialization_vector)
        ciphertext = cipher.encrypt(pad(message.encode("utf-8"), AES.block_size))

        return b64encode(ciphertext).decode("utf-8")

    def aes_decrypt_b64(self, message):
        '''
        Decrypts AES messages sent from the target device.

        Args:
            message (str): The message to decrypt.

        Raises:
            TypeError: One or more arguments is the incorrect type.

        Returns:
            str: The decrypted string.
        '''

        if type(message) is not str:
            raise TypeError("message must be a str value")

        decoded_message = b64decode(message)
        cipher = AES.new(self.aes_common_key, AES.MODE_CBC, self.aes_initialization_vector)
        decrypted_message = unpad(cipher.decrypt(decoded_message), AES.block_size)

        return decrypted_message.decode("utf-8")
