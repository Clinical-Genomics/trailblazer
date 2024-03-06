from trailblazer.clients.authentication_client.dtos.tokens_response import TokensResponse
from trailblazer.clients.authentication_client.google_oauth_client import GoogleOAuthClient
from trailblazer.services.encryption_service.encryption_service import EncryptionService
from trailblazer.store.store import Store


class AuthenticationService:

    def __init__(
        self,
        oauth_client: GoogleOAuthClient,
        encryption_service: EncryptionService,
        store: Store,
    ):
        self.client = oauth_client
        self.encryption_service = encryption_service
        self.store = store

    def exchange_authorization_code(self, authorization_code: str, user_id: int) -> str:
        tokens: TokensResponse = self.client.get_tokens(authorization_code)
        encrypted_token: str = self.encryption_service.encrypt(tokens.refresh_token)
        self.store.update_user_token(user_id=user_id, refresh_token=encrypted_token)
        return tokens.access_token
