from pydantic import BaseModel


class AccessToken(BaseModel):
    access_token: str
