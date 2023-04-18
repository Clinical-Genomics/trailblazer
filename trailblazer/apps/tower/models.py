from datetime import datetime
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, validator

from trailblazer.constants import TOWER_PROCESS_STATUS, TOWER_STATUS, TrailblazerStatus
from trailblazer.utils.datetime import tower_datetime_converter


class TowerTask(BaseModel):
    """NF Tower task model."""

    process: str
    name: str
    status: str
    nativeId: str
    dateCreated: Optional[Union[str, datetime]]
    lastUpdated: Optional[Union[str, datetime]]
    start: Optional[Union[str, datetime]]
    duration: Optional[int]
    hash: Optional[str]
    tag: Optional[str]
    submit: Optional[str]
    complete: Optional[str]
    module: List[str]
    container: Optional[str]
    attempt: Optional[int]
    script: Optional[str]
    scratch: Optional[str]
    workdir: Optional[str]
    queue: Optional[str]
    cpus: Optional[int]
    memory: Optional[int]
    disk: Optional[int]
    time: Optional[int]
    env: Optional[str]
    executor: Optional[str]
    machineType: Optional[str]
    cloudZone: Optional[str]
    priceModel: Optional[str]
    cost: Optional[float]
    errorAction: Optional[str]
    exitStatus: Optional[int]
    realtime: Optional[int]
    pcpu: Optional[float]
    pmem: Optional[float]
    rss: Optional[int]
    vmem: Optional[int]
    peakRss: Optional[int]
    peakVmem: Optional[int]
    rchar: Optional[int]
    wchar: Optional[int]
    syscr: Optional[int]
    syscw: Optional[int]
    readBytes: Optional[int]
    writeBytes: Optional[int]
    volCtxt: Optional[int]
    invCtxt: Optional[int]
    exit: Optional[str]
    id: Optional[int]
    taskId: Optional[int]

    class Config:
        validate_all = True

    @validator("duration")
    def set_duration(cls, duration) -> str:
        return duration or 0

    @validator("status")
    def set_status(cls, status) -> str:
        return TOWER_STATUS.get(status)

    @validator("start", "dateCreated", "lastUpdated")
    def set_datetime(cls, time) -> Optional[Union[str, datetime]]:
        if type(time) is str:
            return tower_datetime_converter(timestamp=time)
        elif type(time) is datetime:
            return time
        else:
            return None

    @property
    def is_complete(cls) -> bool:
        """Returns if the process succeded."""
        return cls.status == TrailblazerStatus.COMPLETED.value


class TowerProcess(BaseModel):
    """NF Tower task model."""

    process: str
    dateCreated: Optional[Union[str, datetime]]
    lastUpdated: Optional[Union[str, datetime]]
    pending: Optional[int]
    submitted: Optional[int]
    running: Optional[int]
    succeeded: Optional[int]
    failed: Optional[int]
    cached: Optional[int]
    memoryEfficiency: Optional[float]
    cpuEfficiency: Optional[float]
    loadCpus: Optional[int]
    loadMemory: Optional[int]
    peakCpus: Optional[int]
    peakTasks: Optional[int]
    peakMemory: Optional[int]

    class Config:
        validate_all = True

    @validator("dateCreated", "lastUpdated")
    def set_datetime(cls, time) -> Optional[Union[str, datetime]]:
        if type(time) is str:
            return tower_datetime_converter(timestamp=time)
        elif type(time) is datetime:
            return time
        else:
            return None

    @property
    def is_complete(cls) -> bool:
        """Returns if the process succeded."""
        return cls.status == TrailblazerStatus.COMPLETED.value

    @property
    def status(cls) -> str:
        for status_flag in TOWER_PROCESS_STATUS.keys():
            if cls.dict().get(status_flag, 0):
                return TOWER_PROCESS_STATUS.get(status_flag)
        return TrailblazerStatus.ERROR.value


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
