from pydantic import BaseModel


class NumberInfo(BaseModel):
    number: int
    set: bool
    infinite: bool


class VersionInfo(BaseModel):
    major: str
    minor: str
    micro: str


class SlurmMeta(BaseModel):
    cluster: str
    release: str
    version: VersionInfo


class PluginInfo(BaseModel):
    accounting_storage: str
    name: str
    type: str
    data_parser: str


class ClientInfo(BaseModel):
    source: str
    user: str
    group: str


class SignalInfo(BaseModel):
    name: str
    id: NumberInfo


class ReturnCodeInfo(BaseModel):
    return_code: NumberInfo
    signal: SignalInfo
    status: list[str]


class JobInfoResponse(BaseModel):
    container: str
    cluster: str
    time_minimum: NumberInfo
    memory_per_tres: str
    scheduled_nodes: str
    minimum_switches: int
    qos: str
    resize_time: NumberInfo
    eligible_time: NumberInfo
    exclusive: list[str]
    cpus_per_tres: str
    preemptable_time: NumberInfo
    tasks: NumberInfo
    system_comment: str
    federation_siblings_active: str
    tasks_per_tres: NumberInfo
    tasks_per_core: NumberInfo
    accrue_time: NumberInfo
    dependency: str
    group_name: str
    profile: list[str]
    priority: NumberInfo
    tres_per_job: str
    failed_node: str
    derived_exit_code: ReturnCodeInfo
    maximum_switch_wait_time: int
    core_spec: int
    mcs_label: str
    required_nodes: str
    tres_bind: str
    user_id: int
    selinux_context: str
    exit_code: ReturnCodeInfo
    federation_origin: str
    container_id: str
    shared: list[str]
    tasks_per_board: NumberInfo
    user_name: str
    flags: list[str]
    standard_input: str
    admin_comment: str
    cores_per_socket: NumberInfo
    job_state: list[str]
    tasks_per_node: NumberInfo
    current_working_directory: str
    standard_error: str
    array_job_id: NumberInfo
    cluster_features: str
    partition: str
    threads_per_core: NumberInfo
    tres_alloc_str: str
    memory_per_cpu: NumberInfo
    cpu_frequency_minimum: NumberInfo
    node_count: NumberInfo
    power: dict
    deadline: NumberInfo
    mail_type: list[str]
    memory_per_node: NumberInfo
    state_reason: str
    het_job_offset: NumberInfo
    end_time: NumberInfo
    sockets_per_board: int
    nice: int
    last_sched_evaluation: NumberInfo
    tres_per_node: str
    burst_buffer: str
    licenses: str
    excluded_nodes: str
    array_max_tasks: NumberInfo
    het_job_id: NumberInfo
    sockets_per_node: NumberInfo
    prefer: str
    time_limit: NumberInfo
    minimum_cpus_per_node: NumberInfo
    tasks_per_socket: NumberInfo
    batch_host: str
    max_cpus: NumberInfo
    job_size_str: list[str]
    cpu_frequency_maximum: NumberInfo
    features: str
    het_job_id_set: str
    state_description: str
    show_flags: list[str]
    array_task_id: NumberInfo
    minimum_tmp_disk_per_node: NumberInfo
    tres_req_str: str
    burst_buffer_state: str
    cron: str
    allocating_node: str
    tres_per_socket: str
    array_task_string: str
    submit_time: NumberInfo
    oversubscribe: bool
    wckey: str
    max_nodes: NumberInfo
    batch_flag: bool
    start_time: NumberInfo
    name: str
    preempt_time: NumberInfo
    contiguous: bool
    job_resources: dict
    billable_tres: NumberInfo
    federation_siblings_viable: str
    cpus_per_task: NumberInfo
    batch_features: str
    thread_spec: int
    cpu_frequency_governor: NumberInfo
    gres_detail: list[str]
    network: str
    restart_cnt: int
    resv_name: str
    extra: str
    delay_boot: NumberInfo
    reboot: bool
    cpus: NumberInfo
    standard_output: str
    pre_sus_time: NumberInfo
    suspend_time: NumberInfo
    association_id: int
    command: str
    tres_freq: str
    requeue: bool
    tres_per_task: str
    mail_user: str
