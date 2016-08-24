# -*- coding: utf-8 -*-
"""
#!/bin/bash -l

set -e

{% if conda_env %}
source activate {{ conda_env }}
{% endif %}

{{ command }}
"""
from datetime import datetime
import logging

from jinja2 import Template

from trailblazer.store import Analysis

log = logging.getLogger(__name__)


def build_pending(case_id, root_dir, seq_type):
    """Create an entry for an analysis which is pending."""
    new_entry = Analysis(
        case_id=case_id,
        pipeline='mip',
        started_at=datetime.now(),
        status='pending',
        root_dir=root_dir,
        type=seq_type,
    )
    return new_entry


def start_mip(analysis_type=None, family_id=None, config=None, ccp=None,
              customer=None, gene_list=None, dryrun=False, executable=None,
              conda_env=None, email=None, analysis_config=None):
    """Start a new analysis for a family.

    Args:
        analysis_type (str): 'exomes' or 'genomes'
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
    if analysis_type:
        assert analysis_type in ('exomes', 'genomes'), 'invalid analysis type'
    if analysis_config is None:
        assert all([analysis_type, family_id, config, ccp])
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

    if analysis_type:
        # type of analysis
        command.append('--analysisType')
        command.append(analysis_type)

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
    template = Template(__doc__)
    script = template.render(command=' '.join(command), conda_env=conda_env)
    return script
