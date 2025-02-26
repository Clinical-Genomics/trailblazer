from keycloak_client import KeycloakOpenID
from keycloak_client import KeycloakGetError
import logging

LOG = logging.getLogger(__name__)


class KeycloakClient:
    """Authentication service to verify tokens against Keycloak and return user information."""

    def __init__(
        self,
        server_url: str,
        client_id: str,
        client_secret: str,
        realm_name: str,
    ):
        """Initialize the AuthenticationService.

        Args:
            user_service (UserService): Service to interact with user data.
            server_url (str): URL to the Keycloak server or container.
            client_id (str): Client ID to use in Keycloak realm.
            client_secret (str): Client secret to use in Keycloak realm.
            realm_name (str): Keycloak realm to connect to.
        """
        self.server_url = server_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.realm_name = realm_name


    def get_client(self) -> KeycloakOpenID:
        """Set the KeycloakOpenID client."""
        try:
            keycloak_openid_client = KeycloakOpenID(
                server_url=self.server_url,
                client_id=self.client_id,
                realm_name=self.realm_name,
                client_secret_key=self.client_secret,
            )
            return keycloak_openid_client
        except KeycloakGetError as e:
            LOG.error(f"Failed to initialize Keycloak client: {e}")
            raise