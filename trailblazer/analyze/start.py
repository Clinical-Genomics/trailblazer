# -*- coding: utf-8 -*-
from datetime import datetime
import logging
import signal
import subprocess

from trailblazer.store import Analysis

log = logging.getLogger(__name__)


def build_pending(case_id, root_dir):
    """Create an entry for an analysis which is pending."""
    new_entry = Analysis(
        case_id=case_id,
        pipeline='mip',
        started_at=datetime.now(),
        status='pending',
        root_dir=root_dir,
    )
    return new_entry


def start_mip(config, family_id=None, ccp=None, gene_list=None,
              dryrun=False, executable=None, email=None, priority='normal'):
    """Start a new analysis for a family.

    Args:
        family_id (str): identifier for the family
        config (path): path to the MIP config file
        ccp (path): cluster constant path to the root of the analysis
        gene_list (Optional[str]): name of gene list in 'references' dir
        conda_env (Optional[str]): conda environment to source
        email (Optional[str]): email to send error mails to

    Returns:
        int: return code from the executed process
    """
    command = []

    # configure executable
    command.append('perl')
    command.append(executable or 'mip.pl')

    # add global config for MIP (could be analysis config)
    command.append('--config_file')
    command.append(config)

    command.append('--slurm_quality_of_service')
    command.append(priority)

    if family_id:
        # add family option
        command.append('--family_id')
        command.append(family_id)

    if email:
        command.append('--email')
        command.append(email)

    if ccp:
        command.append('--cluster_constant_path')
        command.append(ccp)

    if dryrun:
        command.append('--dry_run_all')
        command.append('2')

    if gene_list:
        command.append('--vcfparser_select_file')
        command.append(gene_list)

    log.info("command: %s", ' '.join(command))
    process = subprocess.Popen(
        command,
        preexec_fn=lambda: signal.signal(signal.SIGPIPE, signal.SIG_DFL)
    )
    return process
