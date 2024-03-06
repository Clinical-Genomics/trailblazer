from trailblazer.clients.authentication_client.dtos.tokens_response import TokensResponse
from trailblazer.clients.authentication_client.google_oauth_client import GoogleOAuthClient
from trailblazer.store.store import Store


class AuthenticationService:

    def __init__(self, client: GoogleOAuthClient, store: Store):
        self.client = client
        self.store = store

    def authorize(self, authorization_code: str) -> str:
        tokens: TokensResponse = self.client.get_tokens(authorization_code)

        # 1. Encrypt refresh token
        # 2. Store encrypted refresh token on user
        # 3. Return access token

        return tokens.access_token

    def refresh_access_token(self, user_id: str):
        # 1. Get encrypted refresh token from user
        # 2. Decrypt refresh token
        # 3. Use refresh token to get new access token
        # 4. Encrypt new refresh token
        # 5. Store encrypted refresh token on user
        # 6. Return new access token
        pass
