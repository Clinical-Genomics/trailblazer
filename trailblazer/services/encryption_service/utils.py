import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import os

BLOCK_SIZE = 16
PADDING_SIZE = 128


def encrypt_data(data: str, secret_key: str) -> str:
    padded_data: bytes = _pad_data(data)
    cipher_data: bytes = _encrypt_with_aes(data=padded_data, secret_key=secret_key)
    return bytes_to_string(cipher_data)


def decrypt_data(data: str, secret_key: str) -> str:
    data: bytes = base64.b64decode(data)
    plain_text: bytes = _decrypt_with_aes(data=data, secret_key=secret_key)
    unpadded_plain_text: bytes = _unpad_data(plain_text)
    return unpadded_plain_text.decode()


def _encrypt_with_aes(data: bytes, secret_key: str) -> bytes:
    secret_key = base64.b64decode(secret_key)
    initialization_vector: bytes = os.urandom(BLOCK_SIZE)

    cipher = Cipher(
        algorithms.AES(secret_key),
        modes.CBC(initialization_vector),
        backend=default_backend(),
    )

    encryptor = cipher.encryptor()
    cipher_text: bytes = encryptor.update(data) + encryptor.finalize()
    return initialization_vector + cipher_text


def _decrypt_with_aes(data: bytes, secret_key: str) -> bytes:
    secret_key: bytes = base64.b64decode(secret_key)
    initialization_vector: bytes = data[:BLOCK_SIZE]

    cipher = Cipher(
        algorithms.AES(secret_key),
        modes.CBC(initialization_vector),
        backend=default_backend(),
    )
    decryptor = cipher.decryptor()

    cipher_text: bytes = data[BLOCK_SIZE:]
    plain_text: bytes = decryptor.update(cipher_text) + decryptor.finalize()
    return plain_text


def _pad_data(data: str) -> bytes:
    padder = padding.PKCS7(PADDING_SIZE).padder()
    return padder.update(data.encode()) + padder.finalize()


def _unpad_data(data: bytes) -> bytes:
    unpadder = padding.PKCS7(PADDING_SIZE).unpadder()
    return unpadder.update(data) + unpadder.finalize()


def bytes_to_string(data: bytes) -> str:
    return base64.b64encode(data).decode()
