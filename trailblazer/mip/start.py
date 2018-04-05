# -*- coding: utf-8 -*-
import logging
import signal
import subprocess

from trailblazer.exc import PipelineStartError
from trailblazer.pipeline import Pipeline

LOG = logging.getLogger(__name__)

CLI_OPTIONS = {
    'family': {'option': '--family_id'},
    'config': {'option': '--config_file'},
    'priority': {'option': '--slurm_quality_of_service'},
    'email': {'option': '--email'},
    'base': {'option': '--cluster_constant_path'},
    'dryrun': {
        'option': '--dry_run_all',
        'default': '2',
    },
    'gene_list': {'option': '--vcfparser_select_file'},
    'max_gaussian': {
        'option': '--gatk_variantrecalibration_snv_max_gaussians',
        'default': '1',
    },
    'skip_evaluation': {'option': '--qccollect_skip_evaluation'},
    'start_with': {'option': '--start_with_program'},
}


class MipCli(Pipeline):

    """Wrapper around MIP command line interface."""

    def build_command(self, config, **kwargs):
        """Builds the command to execute MIP."""
        command = ['perl', self.script, CLI_OPTIONS['config']['option'], config]
        for key, value in kwargs.items():
            # enable passing in flags as "False" - shouldn't add command
            if value:
                command.append(CLI_OPTIONS[key]['option'])
                if value is True:
                    command.append(CLI_OPTIONS[key].get('default', '1'))
                else:
                    command.append(value)
        return command

