import logging
from trailblazer.clients.authentication.keycloak_client import KeycloakClient
from trailblazer.services.authentication_service.exceptions import UserNotFoundError, UserRoleError
from trailblazer.services.authentication_service.models import DecodingResponse
from trailblazer.services.user_service.service import UserService
from trailblazer.store.models import User

LOG = logging.getLogger(__name__)


class AuthenticationService:
    """Authentication service to verify tokens against Keycloak and return user information."""

    def __init__(
        self,
        user_service: UserService,
        redirect_uri: str,
        keycloak_client: KeycloakClient,
    ):
        """Initialize the AuthenticationService.

        Args:
            user_service (UserService): Service to interact with user data.
            redirect_uri: Redirect uri for keycloak
            keycloak_client: KeycloakOpenID client.
        """
        self.user_service = user_service
        self.redirect_uri = redirect_uri
        self.client = keycloak_client

    def verify_token(self, jwt_token: str) -> User:
        """Verify the token and return the user if required roles are present.
        Args:
            token (str): The token to verify.

        Returns:
            User: The user object from the statusDB database.

        Raises:
            UserNotFoundError: If the user is not present in the statusDB user table
        """
        try:
            decoded_token = DecodingResponse(**self.client.decode_token(jwt_token))
            self.check_role(decoded_token.realm_access.roles)
            user_email = decoded_token.email
            return self.user_service.get_user_by_email(user_email)
        except ValueError as error:
            raise UserNotFoundError(f"FORBIDDEN: {error}")

    @staticmethod
    def check_role(roles: list[str]) -> None:
        """Check the user roles.
        Currently set to a single permissable role, expand if needed.
        Args:
            roles (list[str]): The user roles received from the RealmAccess.
        Raises:
            UserRoleError: if required role not present
        """
        if not "cg-employee" in roles:
            raise UserRoleError("The user does not have the required role to access this service.")
