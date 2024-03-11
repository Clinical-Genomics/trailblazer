import requests

from trailblazer.clients.authentication_client.dtos.tokens_request import GetTokensRequest
from trailblazer.clients.authentication_client.dtos.tokens_response import TokensResponse
from trailblazer.clients.authentication_client.exceptions import GoogleOAuthClientError


class GoogleOAuthClient:

    def __init__(self, client_id: str, client_secret: str, redirect_uri: str, token_uri: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_uri = token_uri
        self.redirect_uri = redirect_uri

    def get_tokens(self, authorization_code: str) -> TokensResponse:
        """Exchange the authorization code for an access token and refresh token."""
        request = GetTokensRequest(
            client_id=self.client_id,
            client_secret=self.client_secret,
            code=authorization_code,
            redirect_uri=self.redirect_uri,
        )
        data: dict = request.model_dump()

        response = requests.post(self.token_uri, data=data)

        if not response.ok:
            raise GoogleOAuthClientError(response.text)

        return TokensResponse.model_validate(response.json())
