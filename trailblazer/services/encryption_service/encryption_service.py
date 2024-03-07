from trailblazer.services.encryption_service.utils import decrypt_data, encrypt_data


class EncryptionService:
    def __init__(self, secret_key: str):
        self.secret_key = secret_key

    def encrypt(self, data: str) -> str:
        return encrypt_data(data=data, secret_key=self.secret_key)

    def decrypt(self, data: str) -> str:
        return decrypt_data(data=data, secret_key=self.secret_key)
