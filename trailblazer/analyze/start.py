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


def start_mip(family_id=None, config=None, ccp=None, customer=None,
              gene_list=None, dryrun=False, executable=None, conda_env=None,
              email=None, analysis_config=None):
    """Start a new analysis for a family.

    Args:
        family_id (str): identifier for the family
        config (path): path to the MIP config file
        ccp (path): cluster constant path to the root of the analysis
        customer (Optional[str]): customer identifier (instance tag)
        gene_list (Optional[str]): name of gene list in 'references' dir
        conda_env (Optional[str]): conda environment to source
        email (Optional[str]): email to send error mails to

    Returns:
        int: return code from the executed process
    """
    if analysis_config is None:
        assert all([family_id, config, ccp])
    command = []

    # configure executable
    command.append('perl')
    command.append(executable or 'mip.pl')

    if analysis_config:
        # optionally add analysis config
        command.append('--config')
        command.append(analysis_config)

    if config:
        # add YAML config path
        command.append('--configFile')
        command.append(config)

    if ccp:
        # configure the "cluster constant path"
        command.append('--clusterConstantPath')
        command.append(ccp)

    if customer:
        # customer (optional)
        command.append('--instanceTag')
        command.append(customer)

    if family_id:
        # add family option
        command.append('--familyID')
        command.append(family_id)

    if gene_list:
        command.append('--vcfParserSelectFile')
        command.append(gene_list)

    if dryrun:
        command.append('--dryRunAll')
        command.append('2')

    if email:
        command.append('--email')
        command.append(email)

    log.info("command: %s", ' '.join(command))
    process = subprocess.Popen(
        command,
        preexec_fn=lambda: signal.signal(signal.SIGPIPE, signal.SIG_DFL)
    )
    return process
