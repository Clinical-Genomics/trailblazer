from pydantic import BaseModel


class JobInfo(BaseModel):
    account: str | None
    accrue_time: str | None
    admin_comment: str | None
    allocating_node: str | None
    array_job_id: str | None
    array_task_id: str | None
    array_max_tasks: str | None
    array_task_string: str | None
    association_id: int | None
    batch_features: str | None
    batch_flag: bool | None
    batch_host: str | None
    flags: list[str] | None
    burst_buffer: str | None
    burst_buffer_state: str | None
    cluster: str | None
    cluster_features: str | None
    command: str | None
    comment: str | None
    container: str | None
    container_id: str | None
    contiguous: bool | None
    core_spec: int | None
    thread_spec: int | None
    cores_per_socket: str | None
    billable_tres: str | None
    cpus_per_task: str | None
    cpu_frequency_minimum: str | None
    cpu_frequency_maximum: str | None
    cpu_frequency_governor: str | None
    cpus_per_tres: str | None
    cron: str | None
    deadline: str | None
    delay_boot: str | None
    dependency: str | None
    derived_exit_code: str | None
    eligible_time: str | None
    end_time: str | None
    excluded_nodes: str | None
    exit_code: str | None
    extra: str | None
    failed_node: str | None
    features: str | None
    federation_origin: str | None
    federation_siblings_active: str | None
    federation_siblings_viable: str | None
    gres_detail: list[str] | None
    group_id: int | None
    group_name: str | None
    het_job_id: str | None
    het_job_id_set: str | None
    het_job_offset: str | None
    job_id: int | None
    job_resources: str | None
    job_size_str: list[str] | None
    job_state: list[str] | None
    last_sched_evaluation: str | None
    licenses: str | None
    mail_type: list[str] | None
    mail_user: str | None
    max_cpus: str | None
    max_nodes: str | None
    mcs_label: str | None
    memory_per_tres: str | None
    name: str | None
    network: str | None
    nodes: str | None
    nice: int | None
    tasks_per_core: str | None
    tasks_per_tres: str | None
    tasks_per_node: str | None
    tasks_per_socket: str | None
    tasks_per_board: str | None
    cpus: str | None
    node_count: str | None
    tasks: str | None
    partition: str | None
    prefer: str | None
    memory_per_cpu: str | None
    memory_per_node: str | None
    minimum_cpus_per_node: str | None
    minimum_tmp_disk_per_node: str | None
    power: str | None
    preempt_time: str | None
    preemptable_time: str | None
    pre_sus_time: str | None
    priority: str | None
    profile: list[str] | None
    qos: str | None
    reboot: bool | None
    required_nodes: str | None
    minimum_switches: int | None
    requeue: bool | None
    resize_time: str | None
    restart_cnt: int | None
    resv_name: str | None
    scheduled_nodes: str | None
    selinux_context: str | None
    shared: list[str] | None
    exclusive: list[str] | None
    oversubscribe: bool | None
    show_flags: list[str] | None
    sockets_per_board: int | None
    sockets_per_node: str | None
    start_time: str | None
    state_description: str | None
    state_reason: str | None
    standard_error: str | None
    standard_input: str | None
    standard_output: str | None
    submit_time: str | None
    suspend_time: str | None
    system_comment: str | None
    time_limit: str | None
    time_minimum: str | None
    threads_per_core: str | None
    tres_bind: str | None
    tres_freq: str | None
    tres_per_job: str | None
    tres_per_node: str | None
    tres_per_socket: str | None
    tres_per_task: str | None
    tres_req_str: str | None
    tres_alloc_str: str | None
    user_id: int | None
    user_name: str | None
    maximum_switch_wait_time: int | None
    wckey: str | None
    current_working_directory: str | None


class NumberInfo(BaseModel):
    number: int | None = None
    set: bool | None = False
    infinite: bool | None = False


class Error(BaseModel):
    description: str | None = None
    error_number: int | None = None
    error: str | None = None
    source: str | None = None


class Warning(BaseModel):
    description: str | None = None
    source: str | None = None


class JobInfoResponse(BaseModel):
    jobs: list[JobInfo]
    errors: list[Error]
    warnings: list[Warning]
