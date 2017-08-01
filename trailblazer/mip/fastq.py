# -*- coding: utf-8 -*-
from pathlib import Path
import logging
from typing import List

log = logging.getLogger(__name__)


class FastqHandler:

    @staticmethod
    def name_file(lane: int, flowcell: str, sample: str, read: int,
                  undetermined: bool=False) -> str:
        """Name a FASTQ file following MIP conventions."""
        sample = f"{sample}-undetermined" if undetermined else sample
        return f"{lane}_{flowcell}_{sample}_{read}.fastq.gz"

    def link(self, family: str, sample: str, analysis_type: str, files: List[str]):
        """Link FASTQ files for a sample."""
        root_dir = self.families_dir / family / analysis_type / sample / 'fastq'
        root_dir.mkdir(parents=True, exist_ok=True)
        for fastq_data in files:
            fastq_path = Path(fastq_data['path'])
            fastq_name = self.name_file(
                lane=fastq_data['lane'],
                flowcell=fastq_data['flowcell'],
                sample=sample,
                read=fastq_data['read'],
                undetermined=fastq_data['undetermined'],
            )
            dest_path = root_dir / fastq_name
            if not dest_path.exists():
                log.info(f"linking: {fastq_path} -> {dest_path}")
                dest_path.symlink_to(fastq_path)
            else:
                log.debug(f"destination path already exists: {dest_path}")
