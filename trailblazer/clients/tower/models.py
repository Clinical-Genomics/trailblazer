from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator

from trailblazer.constants import (
    TOWER_PROCESS_STATUS,
    TOWER_TASK_STATUS,
    SlurmJobStatus,
    TrailblazerStatus,
)
from trailblazer.utils.datetime import tower_datetime_converter

SCALE_TO_MILLISEC: int = 1000


class TowerTask(BaseModel):
    """NF Tower task model."""

    process: str
    name: str
    status: str
    nativeId: str
    dateCreated: str | datetime | None = None
    lastUpdated: str | datetime | None = None
    start: str | datetime | None = None
    duration: int | None = None
    hash: str | None = None
    tag: str | None = None
    submit: str | None = None
    complete: str | None = None
    module: list[str]
    container: str | None = None
    attempt: int | None = None
    script: str | None = None
    scratch: str | None = None
    workdir: str | None = None
    queue: str | None = None
    cpus: int | None = None
    memory: int | None = None
    disk: int | None = None
    time: int | None = None
    env: str | None = None
    executor: str | None = None
    machineType: str | None = None
    cloudZone: str | None = None
    priceModel: str | None = None
    cost: float | None = None
    errorAction: str | None = None
    exitStatus: int | None = None
    realtime: int | None = None
    pcpu: float | None = None
    pmem: float | None = None
    rss: int | None = None
    vmem: int | None = None
    peakRss: int | None = None
    peakVmem: int | None = None
    rchar: int | None = None
    wchar: int | None = None
    syscr: int | None = None
    syscw: int | None = None
    readBytes: int | None = None
    writeBytes: int | None = None
    volCtxt: int | None = None
    invCtxt: int | None = None
    exit: str | None = None
    id: int | None = None
    taskId: int | None = None
    model_config = ConfigDict(validate_default=True)

    @field_validator("duration")
    @classmethod
    def set_duration(cls, raw_duration: int | None) -> int:
        """Convert milliseconds to seconds or return 0 if empty."""
        return round(raw_duration / SCALE_TO_MILLISEC) if raw_duration else 0

    @field_validator("status")
    @classmethod
    def set_status(cls, raw_status) -> str:
        return TOWER_TASK_STATUS.get(raw_status)

    @field_validator("start", "dateCreated", "lastUpdated")
    @classmethod
    def set_datetime(cls, raw_time) -> str | datetime | None:
        if isinstance(raw_time, str):
            return tower_datetime_converter(datetime_stamp=raw_time)
        elif isinstance(raw_time, datetime):
            return raw_time
        else:
            return None

    @property
    def is_complete(cls) -> bool:
        """Returns if the process succeded."""
        return cls.status == SlurmJobStatus.COMPLETED


class TowerProcess(BaseModel):
    """NF Tower task model."""

    process: str
    dateCreated: str | datetime | None = None
    lastUpdated: str | datetime | None = None
    pending: int | None = None
    submitted: int | None = None
    running: int | None = None
    succeeded: int | None = None
    failed: int | None = None
    cached: int | None = None
    memoryEfficiency: float | None = None
    cpuEfficiency: float | None = None
    loadCpus: int | None = None
    loadMemory: int | None = None
    peakCpus: int | None = None
    peakTasks: int | None = None
    peakMemory: int | None = None
    model_config = ConfigDict(validate_default=True)

    @field_validator("dateCreated", "lastUpdated")
    @classmethod
    def set_datetime(cls, raw_time) -> str | datetime | None:
        if isinstance(raw_time, str):
            return tower_datetime_converter(datetime_stamp=raw_time)
        elif isinstance(raw_time, datetime):
            return raw_time
        else:
            return None

    @property
    def is_complete(cls) -> bool:
        """Returns if the process succeded."""
        return cls.status == TrailblazerStatus.COMPLETED

    @property
    def status(cls) -> str:
        for status_flag in TOWER_PROCESS_STATUS.keys():
            if cls.model_dump().get(status_flag, 0):
                return TOWER_PROCESS_STATUS.get(status_flag)
        return TrailblazerStatus.ERROR


class TowerWorkflow(BaseModel):
    """NF Tower workflow model."""

    status: str


class TowerProgress(BaseModel):
    """NF Tower progress model."""

    workflowProgress: dict
    processesProgress: list


class TowerTaskResponse(BaseModel):
    """NF Tower task response model."""

    tasks: list[dict[str, TowerTask]] | None
    total: int


class TowerWorkflowResponse(BaseModel):
    """NF Tower task model."""

    workflow: TowerWorkflow
    progress: TowerProgress
