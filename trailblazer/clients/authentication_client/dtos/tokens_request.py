from pydantic import BaseModel


class GetTokensRequest(BaseModel):
    cliend_id: str
    client_secret: str
    code: str
    grant_type: str = "authorization_code"
    redirect_uri: str
