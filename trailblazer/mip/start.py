# -*- coding: utf-8 -*-
import logging
import signal
import subprocess

from trailblazer.exc import MipStartError

LOG = logging.getLogger(__name__)

CLI_OPTIONS = {
    "config": {"option": "--config_file"},
    "priority": {"option": "--slurm_quality_of_service"},
    "email": {"option": "--email"},
    "base": {"option": "--cluster_constant_path"},
    "dryrun": {"option": "--dry_run_all"},
    "gene_list": {"option": "--vcfparser_slt_fl"},
    "max_gaussian": {"option": "--gatk_varrecal_snv_max_gau"},
    "skip_evaluation": {"option": "--qccollect_skip_evaluation"},
    "start_with": {"option": "--start_with_recipe"},
}


class MipCli(object):

    """Wrapper around MIP command line interface."""

    def __init__(self, script, pipeline, conda_env):
        """Initialize MIP command line interface."""
        self.script = script
        self.pipeline = pipeline
        self.conda_env = conda_env
