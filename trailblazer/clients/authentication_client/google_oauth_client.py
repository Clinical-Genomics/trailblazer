import requests

from trailblazer.clients.authentication_client.dtos.refresh_token_request import (
    RefreshAccessTokenRequest,
)
from trailblazer.clients.authentication_client.dtos.tokens_request import GetTokensRequest
from trailblazer.clients.authentication_client.dtos.tokens_response import TokensResponse
from trailblazer.clients.authentication_client.exceptions import GoogleOAuthClientError


class GoogleOAuthClient:
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str, oauth_base_url: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.oauth_base_url = oauth_base_url
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

        response = requests.post(self.oauth_base_url, data=data)

        if not response.ok:
            raise GoogleOAuthClientError(response.text)

        return TokensResponse.model_validate(response.json())

    def get_id_token(self, refresh_token: str) -> str:
        """Use refresh token to get a new id token."""
        request = RefreshAccessTokenRequest(
            client_id=self.client_id,
            client_secret=self.client_secret,
            refresh_token=refresh_token,
        )
        data: str = request.model_dump_json()

        response = requests.post(self.oauth_base_url, data=data)

        if not response.ok:
            raise GoogleOAuthClientError(response.text)

        return response.json()["id_token"]
