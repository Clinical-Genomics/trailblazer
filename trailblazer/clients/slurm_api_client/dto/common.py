from pydantic import BaseModel


class SlurmError(BaseModel):
    description: str | None = None
    error_number: int | None = None
    error: str | None = None
    source: str | None = None


class SlurmWarning(BaseModel):
    description: str | None = None
    source: str | None = None


class NumberWithFlags(BaseModel):
    set: bool | None = None
    infinite: bool | None = None
    number: int | None = None


class JobResources(BaseModel):
    nodes: str | None = None
    allocated_cores: int | None = None
    allocated_cpus: int | None = None
    allocated_hosts: int | None = None
    allocated_nodes: list[str] | None = None


class ExitCodeSignal(BaseModel):
    id: NumberWithFlags | None = None
    name: str | None = None


class ExitCode(BaseModel):
    status: list[str] | None = None
    return_code: NumberWithFlags | None = None
    signal: ExitCodeSignal | None = None


class SlurmJobInfo(BaseModel):
    account: str | None = None
    accrue_time: NumberWithFlags | None = None
    admin_comment: str | None = None
    allocating_node: str | None = None
    array_job_id: NumberWithFlags | None = None
    array_task_id: NumberWithFlags | None = None
    array_max_tasks: NumberWithFlags | None = None
    array_task_string: str | None = None
    association_id: int | None = None
    batch_features: str | None = None
    batch_flag: bool | None = None
    batch_host: str | None = None
    flags: list[str] | None = None
    burst_buffer: str | None = None
    burst_buffer_state: str | None = None
    cluster: str | None = None
    cluster_features: str | None = None
    command: str | None = None
    comment: str | None = None
    container: str | None = None
    container_id: str | None = None
    contiguous: bool | None = None
    core_spec: int | None = None
    thread_spec: int | None = None
    cores_per_socket: NumberWithFlags | None = None
    billable_tres: NumberWithFlags | None = None
    cpus_per_task: NumberWithFlags | None = None
    cpu_frequency_minimum: NumberWithFlags | None = None
    cpu_frequency_maximum: NumberWithFlags | None = None
    cpu_frequency_governor: NumberWithFlags | None = None
    cpus_per_tres: str | None = None
    cron: str | None = None
    deadline: NumberWithFlags | None = None
    delay_boot: NumberWithFlags | None = None
    dependency: str | None = None
    derived_exit_code: ExitCode | None = None
    eligible_time: NumberWithFlags | None = None
    end_time: NumberWithFlags | None = None
    excluded_nodes: str | None = None
    exit_code: ExitCode | None = None
    extra: str | None = None
    failed_node: str | None = None
    features: str | None = None
    federation_origin: str | None = None
    federation_siblings_active: str | None = None
    federation_siblings_viable: str | None = None
    gres_detail: list[str] | None = None
    group_id: int | None = None
    group_name: str | None = None
    het_job_id: NumberWithFlags | None = None
    het_job_id_set: str | None = None
    het_job_offset: NumberWithFlags | None = None
    job_id: int | None = None
    job_resources: JobResources | None = None
    job_size_str: list[str] | None = None
    job_state: list[str] | None = None
    last_sched_evaluation: NumberWithFlags | None = None
    licenses: str | None = None
    mail_type: list[str] | None = None
    mail_user: str | None = None
    max_cpus: NumberWithFlags | None = None
    max_nodes: NumberWithFlags | None = None
    mcs_label: str | None = None
    memory_per_tres: str | None = None
    name: str | None = None
    network: str | None = None
    nodes: str | None = None
    nice: int | None = None
    tasks_per_core: NumberWithFlags | None = None
    tasks_per_tres: NumberWithFlags | None = None
    tasks_per_node: NumberWithFlags | None = None
    tasks_per_socket: NumberWithFlags | None = None
    tasks_per_board: NumberWithFlags | None = None
    cpus: NumberWithFlags | None = None
    node_count: NumberWithFlags | None = None
    tasks: NumberWithFlags | None = None
    partition: str | None = None
    prefer: str | None = None
    memory_per_cpu: NumberWithFlags | None = None
    memory_per_node: NumberWithFlags | None = None
    minimum_cpus_per_node: NumberWithFlags | None = None
    minimum_tmp_disk_per_node: NumberWithFlags | None = None
    power: list[str] | None = None
    preempt_time: NumberWithFlags | None = None
    preemptable_time: NumberWithFlags | None = None
    pre_sus_time: NumberWithFlags | None = None
    priority: NumberWithFlags | None = None
    profile: list[str] | None = None
    qos: str | None = None
    reboot: bool | None = None
    required_nodes: str | None = None
    minimum_switches: int | None = None
    requeue: bool | None = None
    resize_time: NumberWithFlags | None = None
    restart_cnt: int | None = None
    resv_name: str | None = None
    scheduled_nodes: str | None = None
    selinux_context: str | None = None
    shared: list[str] | None = None
    exclusive: list[str] | None = None
    oversubscribe: bool | None = None
    show_flags: list[str] | None = None
    sockets_per_board: int | None = None
    sockets_per_node: NumberWithFlags | None = None
    start_time: NumberWithFlags | None = None
    state_description: str | None = None
    state_reason: str | None = None
    standard_error: str | None = None
    standard_input: str | None = None
    standard_output: str | None = None
    submit_time: NumberWithFlags | None = None
    suspend_time: NumberWithFlags | None = None
    system_comment: str | None = None
    time_limit: NumberWithFlags | None = None
    time_minimum: NumberWithFlags | None = None
    threads_per_core: NumberWithFlags | None = None
    tres_bind: str | None = None
    tres_freq: str | None = None
    tres_per_job: str | None = None
    tres_per_node: str | None = None
    tres_per_socket: str | None = None
    tres_per_task: str | None = None
    tres_req_str: str | None = None
    tres_alloc_str: str | None = None
    user_id: int | None = None
    user_name: str | None = None
    maximum_switch_wait_time: int | None = None
    wckey: str | None = None
    current_working_directory: str | None = None
