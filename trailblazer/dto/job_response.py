from pydantic import BaseModel

from trailblazer.constants import JobType


class JobResponse(BaseModel):
    name: str
