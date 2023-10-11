from datetime import datetime
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, ConfigDict, field_validator

from trailblazer.constants import (
    TOWER_PROCESS_STATUS,
    TOWER_TASK_STATUS,
    TOWER_WORKFLOW_STATUS,
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
    dateCreated: Optional[Union[str, datetime]] = None
    lastUpdated: Optional[Union[str, datetime]] = None
    start: Optional[Union[str, datetime]] = None
    duration: Optional[int] = None
    hash: Optional[str] = None
    tag: Optional[str] = None
    submit: Optional[str] = None
    complete: Optional[str] = None
    module: List[str]
    container: Optional[str] = None
    attempt: Optional[int] = None
    script: Optional[str] = None
    scratch: Optional[str] = None
    workdir: Optional[str] = None
    queue: Optional[str] = None
    cpus: Optional[int] = None
    memory: Optional[int] = None
    disk: Optional[int] = None
    time: Optional[int] = None
    env: Optional[str] = None
    executor: Optional[str] = None
    machineType: Optional[str] = None
    cloudZone: Optional[str] = None
    priceModel: Optional[str] = None
    cost: Optional[float] = None
    errorAction: Optional[str] = None
    exitStatus: Optional[int] = None
    realtime: Optional[int] = None
    pcpu: Optional[float] = None
    pmem: Optional[float] = None
    rss: Optional[int] = None
    vmem: Optional[int] = None
    peakRss: Optional[int] = None
    peakVmem: Optional[int] = None
    rchar: Optional[int] = None
    wchar: Optional[int] = None
    syscr: Optional[int] = None
    syscw: Optional[int] = None
    readBytes: Optional[int] = None
    writeBytes: Optional[int] = None
    volCtxt: Optional[int] = None
    invCtxt: Optional[int] = None
    exit: Optional[str] = None
    id: Optional[int] = None
    taskId: Optional[int] = None
    model_config = ConfigDict(validate_default=True)

    @field_validator("duration")
    @classmethod
    def set_duration(cls, raw_duration: Optional[int]) -> int:
        """Convert milliseconds to seconds or return 0 if empty."""
        return round(raw_duration / SCALE_TO_MILLISEC) if raw_duration else 0

    @field_validator("status")
    @classmethod
    def set_status(cls, raw_status) -> str:
        return TOWER_TASK_STATUS.get(raw_status)

    @field_validator("start", "dateCreated", "lastUpdated")
    @classmethod
    def set_datetime(cls, raw_time) -> Optional[Union[str, datetime]]:
        if type(raw_time) is str:
            return tower_datetime_converter(datetime_stamp=raw_time)
        elif type(raw_time) is datetime:
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
    dateCreated: Optional[Union[str, datetime]] = None
    lastUpdated: Optional[Union[str, datetime]] = None
    pending: Optional[int] = None
    submitted: Optional[int] = None
    running: Optional[int] = None
    succeeded: Optional[int] = None
    failed: Optional[int] = None
    cached: Optional[int] = None
    memoryEfficiency: Optional[float] = None
    cpuEfficiency: Optional[float] = None
    loadCpus: Optional[int] = None
    loadMemory: Optional[int] = None
    peakCpus: Optional[int] = None
    peakTasks: Optional[int] = None
    peakMemory: Optional[int] = None
    model_config = ConfigDict(validate_default=True)

    @field_validator("dateCreated", "lastUpdated")
    @classmethod
    def set_datetime(cls, raw_time) -> Optional[Union[str, datetime]]:
        if type(raw_time) is str:
            return tower_datetime_converter(datetime_stamp=raw_time)
        elif type(raw_time) is datetime:
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
            if cls.dict().get(status_flag, 0):
                return TOWER_PROCESS_STATUS.get(status_flag)
        return TrailblazerStatus.ERROR


class TowerWorkflow(BaseModel):
    """NF Tower workflow model."""

    status: str


class TowerProgress(BaseModel):
    """NF Tower progress model."""

    workflowProgress: Dict
    processesProgress: List


class TowerTaskResponse(BaseModel):
    """NF Tower task response model."""

    tasks: List[Optional[Dict[str, TowerTask]]]
    total: int


class TowerWorkflowResponse(BaseModel):
    """NF Tower task model."""

    workflow: TowerWorkflow
    progress: TowerProgress
