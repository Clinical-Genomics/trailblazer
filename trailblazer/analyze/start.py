# -*- coding: utf-8 -*-
"""
#!/bin/bash -l

set -e

{% if conda_env %}
source activate {{ conda_env }}
{% endif %}

{{ command }}
"""
import logging

from jinja2 import Template

log = logging.getLogger(__name__)


def start_mip(analysis_type, family_id, config, ccp, customer=None,
              gene_list=None, dryrun=False, executable=None, conda_env=None,
              email=None):
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
    assert analysis_type in ('exomes', 'genomes'), 'invalid analysis type'
    command = []

    # configure executable
    command.append('perl')
    command.append(executable or 'mip.pl')

    # add YAML config path
    command.append('--configFile')
    command.append(config)

    # type of analysis
    command.append('--analysisType')
    command.append(analysis_type)

    # configure the "cluster constant path"
    command.append('--clusterConstantPath')
    command.append(ccp)

    # customer (optional)
    command.append('--instanceTag')
    command.append(customer)

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
