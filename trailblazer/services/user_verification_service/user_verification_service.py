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

    def __init__(self, store: Store, google_client_id: str, google_api_base_url: str):
        self.store: Store = store
        self.google_client_id: str = google_client_id
        self.google_api_base_url: str = google_api_base_url

    def verify_user(self, authorization_header: str) -> User:
        """Verify the user by checking if the JWT token provided is valid."""
        jwt_token: str = self._extract_token_from_header(authorization_header)
        google_certs: Mapping = self._get_google_certs()
        try:
            payload: Mapping = jwt.decode(
                token=jwt_token,
                certs=google_certs,
                verify=True,
                audience=self.google_client_id,
            )
        except Exception as error:
            raise UserTokenVerificationError(f"{error}") from error
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

    def _get_google_certs(self) -> Mapping:
        """Get the Google certificates."""
        try:
            # Fetch the Google public keys. Google oauth uses v1 certs.
            response = requests.get(self.google_api_base_url + "/oauth2/v1/certs")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise GoogleCertsError("Failed to fetch Google public keys") from e

    def _get_user(self, user_email: str) -> User:
        """Check if the user is known."""
        if user := self.store.get_user(email=user_email, exclude_archived=True):
            return user
        raise ValueError("User not found in the database")
