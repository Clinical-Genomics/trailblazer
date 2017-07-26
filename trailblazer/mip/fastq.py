# -*- coding: utf-8 -*-
from pathlib import Path
import logging
from typing import List

log = logging.getLogger(__name__)


class FastqHandler:

    def link(self, family: str, sample: str, analysis_type: str, files: List[str]):
        """Link FASTQ files for a sample."""
        root_dir = self.families_dir / family / analysis_type / sample / 'fastq'
        root_dir.mkdir(parents=True, exist_ok=True)
        for fastq in files:
            fastq_path = Path(fastq)
            dest_path = root_dir / fastq_path.name
            log.info(f"linking: {fastq_path} -> {dest_path}")
            fastq_path.symlink_to(dest_path)
