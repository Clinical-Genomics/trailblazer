from typing import Mapping

from google.auth import jwt
import requests

from trailblazer.services.user_verification_service.exc import (
    GoogleCertsError,
    UserTokenVerificationError,
)
from trailblazer.store.models import User
from trailblazer.store.store import Store


class UserVerificationService:
    """Service to verify the user."""

    def __init__(self, store: Store, oauth_clinet_id: str):
        self.store: Store = store
        self.oauth_client_id: str = oauth_clinet_id

    def verify_user(self, authorization_header: str) -> User:
        """Verify the user by checking if the JWT token provided is valid."""
        jwt_token: str = self._extract_token_from_header(authorization_header)
        google_certs: Mapping = self._get_google_certs(jwt_token)
        try:
            payload: Mapping = jwt.decode(
                token=jwt_token,
                certs=google_certs,
                verify=True,
                audience=[self.oauth_client_id, "CG-TB-CLIENT"],
            )
        except Exception as error:
            raise UserTokenVerificationError(
                "Could not verify user token. It might be false or expired."
            ) from error
        user_email: str = payload["email"]
        return self._get_user(user_email)

    @staticmethod
    def _extract_token_from_header(authorization_header: str) -> str:
        """Extract the token from the authorization header.
        args: authorization_header: The authorization header.
        raises ValueError: If no authorization header is provided.
        """
        if authorization_header:
            jwt_token = authorization_header.split("Bearer ")[-1]
            return jwt_token
        raise ValueError("No authorization header provided with request")

    @staticmethod
    def _get_certs_url(jwt_token: str) -> str:
        """
        Get the URL to fetch the Google certificates.
        If the email present in the payload belongs to a Google service account then return the URL for service accounts.
        Else it uses the URL for OAuth2.
        """
        decoded_token = jwt.decode(token=jwt_token, verify=False)
        email: str = decoded_token.get("email")
        if not email:
            raise UserTokenVerificationError("Email claim not found in the token.")
        if email.endswith("gserviceaccount.com"):
            return f"https://www.googleapis.com/robot/v1/metadata/x509/{email}"
        return "https://www.googleapis.com/oauth2/v1/certs"

    def _get_google_certs(self, jwt_token: str) -> Mapping:
        """Get the Google certificates."""
        url = self._get_certs_url(jwt_token)
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise GoogleCertsError("Failed to fetch Google certs") from e

    def _get_user(self, user_email: str) -> User:
        """Check if the user is known."""
        if user := self.store.get_user(email=user_email, exclude_archived=True):
            return user
        raise ValueError("User not found in the database")
