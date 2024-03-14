from trailblazer.clients.authentication_client.dtos.tokens_response import TokensResponse
from trailblazer.clients.authentication_client.google_oauth_client import GoogleOAuthClient
from trailblazer.clients.google_api_client.google_api_client import GoogleAPIClient
from trailblazer.services.authentication_service.exceptions import UserNotFoundError
from trailblazer.services.encryption_service.encryption_service import EncryptionService
from trailblazer.store.models import User
from trailblazer.store.store import Store


class AuthenticationService:
    def __init__(
        self,
        google_oauth_client: GoogleOAuthClient,
        google_api_client: GoogleAPIClient,
        encryption_service: EncryptionService,
        store: Store,
    ):
        self.google_oauth_client = google_oauth_client
        self.google_api_client = google_api_client
        self.encryption_service = encryption_service
        self.store = store

    def authenticate(self, authorization_code: str) -> str:
        """Exchange the authorization code for an id token."""
        tokens: TokensResponse = self.google_oauth_client.get_tokens(authorization_code)
        user_email: str = self.google_api_client.get_user_email(tokens.access_token)
        user: User | None = self.store.get_user(user_email)

        if not user:
            raise UserNotFoundError

        encrypted_token: str = self.encryption_service.encrypt(tokens.refresh_token)
        self.store.update_user_token(user_id=user.id, refresh_token=encrypted_token)

        return tokens.id_token

    def refresh_token(self, user_id: int) -> str:
        """Retrieve a refreshed id token for the user."""
        user: User = self.store.get_user_by_id(user_id)
        refresh_token: str = self.encryption_service.decrypt(user.refresh_token)
        id_token: str = self.google_oauth_client.get_id_token(refresh_token)
        return id_token
