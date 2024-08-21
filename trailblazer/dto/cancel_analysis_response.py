from pydantic import BaseModel


class CancelAnalysisResponse(BaseModel):
    message: str
