from pydantic import BaseModel


class RefreshAccessTokenRequest(BaseModel):
    client_id: str
    client_secret: str
    refresh_token: str
    grant_type: str = "refresh_token"
