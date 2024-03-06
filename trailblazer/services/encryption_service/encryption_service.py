class EncryptionService:
    def __init__(self, secret_key: str):
        self.secret_key = secret_key

    def encrypt(self, data: str) -> str:
        return data

    def decrypt(self, data: str) -> str:
        return data
