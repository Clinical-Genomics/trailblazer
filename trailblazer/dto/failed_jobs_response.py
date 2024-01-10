from pydantic import BaseModel


class FailedJobCategoryStatistics(BaseModel):
    name: str
    count: int


class FailedJobsResponse(BaseModel):
    jobs: list[FailedJobCategoryStatistics]
