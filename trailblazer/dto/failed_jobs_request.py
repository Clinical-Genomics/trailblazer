from pydantic import BaseModel

from trailblazer.constants import ONE_MONTH_IN_DAYS


class FailedJobsRequest(BaseModel):
    days_back: int | None = ONE_MONTH_IN_DAYS
