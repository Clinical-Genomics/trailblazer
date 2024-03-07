from trailblazer.services.encryption_service.encryption_service import EncryptionService


def test_encryption(encryption_service: EncryptionService):
    # GIVEN a plain text
    plain_text = "my secret"

    # WHEN encrypting and decrypting the plain text
    encrypted_text: str = encryption_service.encrypt(plain_text)
    decrypted_text: str = encryption_service.decrypt(encrypted_text)

    # THEN the decrypted text is the same as the plain text
    assert decrypted_text == plain_text

    # THEN the encrypted text is different from the plain text
    assert encrypted_text != plain_text
