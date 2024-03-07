from pydantic import BaseModel


class CodeExchangeRequest(BaseModel):
    code: str
