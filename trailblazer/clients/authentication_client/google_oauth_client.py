import requests

from trailblazer.clients.authentication_client.dtos.tokens_request import GetTokensRequest
from trailblazer.clients.authentication_client.dtos.tokens_response import TokensResponse
from trailblazer.clients.authentication_client.exceptions import GoogleOAuthClientError


class GoogleOAuthClient:

    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_uri = "https://oauth2.googleapis.com/token"
        self.redirect_uri = redirect_uri

    def get_tokens(self, authorization_code: str):
        request = GetTokensRequest(
            cliend_id=self.client_id,
            client_secret=self.client_secret,
            code=authorization_code,
            redirect_uri=self.redirect_uri,
        )
        data: str = request.model_dump_json()

        response = requests.post(self.token_uri, data=data)

        if not response.ok:
            raise GoogleOAuthClientError(response.text)

        return TokensResponse.model_validate(response.json())
