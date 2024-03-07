import base64
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

NONCE_SIZE = 12


def encrypt_data(data: str, secret_key: str) -> str:
    data_bytes: bytes = data.encode()
    cipher_data: bytes = _encrypt_with_aes(data=data_bytes, secret_key=secret_key)
    return bytes_to_string(cipher_data)


def decrypt_data(data: str, secret_key: str) -> str:
    data: bytes = base64.b64decode(data)
    plain_text_bytes: bytes = _decrypt_with_aes(data=data, secret_key=secret_key)
    return plain_text_bytes.decode()


def _encrypt_with_aes(data: bytes, secret_key: str) -> bytes:
    cipher = AESGCM(base64.b64decode(secret_key))
    nonce: bytes = os.urandom(NONCE_SIZE)
    cipher_text: bytes = cipher.encrypt(nonce=nonce, data=data, associated_data=None)
    return nonce + cipher_text


def _decrypt_with_aes(data: bytes, secret_key: str) -> bytes:
    cipher = AESGCM(base64.b64decode(secret_key))
    nonce: bytes = data[:NONCE_SIZE]
    cipher_text: bytes = data[NONCE_SIZE:]
    return cipher.decrypt(nonce=nonce, data=cipher_text, associated_data=None)


def bytes_to_string(data: bytes) -> str:
    return base64.b64encode(data).decode()
