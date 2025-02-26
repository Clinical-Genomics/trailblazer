from keycloak import KeycloakAuthenticationError, KeycloakGetError
import logging

from trailblazer.clients.authentication.keycloak_client import KeycloakClient
from trailblazer.services.user_service.service import UserService
from trailblazer.store.models import User

LOG = logging.getLogger(__name__)


class AuthenticationService:
    """Authentication service to verify tokens against Keycloak and return user information."""

    def __init__(
        self,
        user_service: UserService,
        keycloak_client: KeycloakClient,
        redirect_uri: str,
    ):
        """Initialize the AuthenticationService.

        Args:
            user_service (UserService): Service to interact with user data.
            keycloak_client (KeycloakClient): Keycloak client to interact with Keycloak.
            redirect_uri (str): Redirect URI to use.
        """
        self.user_service = user_service
        self.redirect_uri = redirect_uri
        self.client = keycloak_client

    def verify_token(self, token: str) -> User:
        """Verify the token and return the user.

        Args:
            token (str): The token to verify.

        Returns:
            User: The user object from the statusDB database.

        Raises:
            ValueError: If the token is not active.
        """
        try:
            token_info = self.client.introspect(token)
            if not token_info["active"]:
                raise ValueError("Token is not active")
            verified_token = self.client.decode_token(token)
            user_email = verified_token["email"]
            return self.user_service.get_user_by_email(user_email)
        except KeycloakAuthenticationError as e:
            LOG.error(f"Token verification failed: {e}")
            raise

    def get_auth_url(self) -> str:
        """Get the authentication URL."""
        try:
            auth_url = self.client.auth_url(
                redirect_uri=self.redirect_uri, scope="openid profile email"
            )
            LOG.debug(f"Auth URL: {auth_url}")
            return auth_url
        except KeycloakGetError as e:
            LOG.error(f"Failed to get auth URL: {e}")
            raise

    def logout_user(self, refresh_token: str):
        """Logout the user.

        Args:
            refresh_token (str): The refresh token for the user in the current session.
        """
        try:
            self.client.logout(refresh_token)
        except KeycloakAuthenticationError as e:
            LOG.error(f"Logout failed: {e}")
            raise

    def get_user_info(self, token: dict) -> dict:
        """Get the user information.

        Args:
            token (dict): The token dictionary containing the access token.

        Returns:
            dict: The user information.
        """
        try:
            return self.client.userinfo(token["access_token"])
        except KeycloakGetError as e:
            LOG.error(f"Failed to get user info: {e}")
            raise

    def get_token(self, code: str) -> dict:
        """Get the user token.

        Args:
            code (str): The authorization code.

        Returns:
            dict: The token dictionary.
        """
        try:
            return self.client.token(
                grant_type="authorization_code", code=code, redirect_uri=self.redirect_uri
            )
        except KeycloakAuthenticationError as e:
            LOG.error(f"Failed to get token: {e}")
            raise

    def check_user_role(self, token: str, required_role: str) -> None:
        """Check if the user has the required role.

        Args:
            token (str): The user token.
            required_role (str): The role to check.

        Returns:
            None

        Raises:
            KeycloakAuthenticationError: If the user does not have the required role.
        """
        verified_token = self.client.decode_token(token)
        roles = verified_token.get("realm_access", {}).get("roles", [])
        if not required_role in roles:
            raise KeycloakAuthenticationError("User does not have the required role.")
        LOG.debug(f"User has the required role: {required_role}")
