from pydantic import BaseModel


class CancelAnalysisResponse(BaseModel):
    message: str = "Analysis cancelled successfully."
