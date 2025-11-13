from keycloak import KeycloakOpenID
from keycloak.exceptions import KeycloakConnectionError


class KeycloakClient:
    def __init__(self, server_url, client_id, realm_name, client_secret_key, redirect_uri):
        self.client_id = client_id
        self.client_secret_key = client_secret_key
        self.realm_name = realm_name
        self.redirect_uri = redirect_uri
        self.server_url = server_url
        self._client_instance: KeycloakOpenID | None = None

    def get_client(self) -> KeycloakOpenID:
        if self._client_instance is None:
            try:
                self._client_instance = KeycloakOpenID(
                    server_url=self.server_url,
                    client_id=self.client_id,
                    realm_name=self.realm_name,
                    client_secret_key=self.client_secret_key,
                )
            except KeycloakConnectionError as error:
                raise KeycloakConnectionError(f"Failed to connect to Keycloak: {error}")
            except Exception as error:
                raise Exception(f"An error occurred while creating Keycloak client: {error}")
        return self._client_instance

    def decode_token(self, access_token: str) -> dict:
        """Decode an access token.
        Args:
            access_token: An jwt access token.
        """
        client: KeycloakOpenID = self.get_client()
        return client.decode_token(token=access_token)
