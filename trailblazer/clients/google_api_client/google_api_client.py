import requests

from trailblazer.clients.google_api_client.exceptions import GoogleAPIClientError


class GoogleAPIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def _get_headers(self, access_token: str) -> dict:
        return {"Authorization": f"Bearer {access_token}"}

    def get_user_email(self, access_token: str) -> str:
        """Get the user email for the given access token."""
        endpoint: str = f"{self.base_url}/oauth2/v1/userinfo"
        headers: dict = self._get_headers(access_token)
        response = requests.get(endpoint, headers=headers)

        if not response.ok:
            raise GoogleAPIClientError(response.text)

        return response.json()["email"]
