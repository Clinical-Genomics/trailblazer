# -*- coding: utf-8 -*-
import datetime as dt
import logging
import os
from typing import List

log = logging.getLogger(__name__)


class FastqHandler:

    def fastq_name(sample: str, lane: int, date: dt.datetime, flowcell: str, tile: int, read: int,
                   undetermined: bool=False) -> str:
        """Name a FASTQ file according to MIP conventions."""
        template = "{lane}_{date}_{flowcell}-{tile}-{sample}_{read}.fastq.gz"
        sample = f"Undetermined-{sample}" if undetermined else sample
        mip_name = template.format(
            lane=lane,
            date=date.date().isoformat().replace('-', ''),
            flowcell=flowcell,
            tile=tile,
            sample=sample,
            read=read,
        )
        return mip_name

    def link(self, family: str, sample: str, analysis_type: str, files: List[dict],
             dry: bool=False):
        """Link FASTQ files for a sample."""
        root_dir = self.families_dir / family / analysis_type / sample / 'fastq'
        if not dry:
            root_dir.mkdir(parents=True, exist_ok=True)
        for fastq in files:
            dest_name = self.fastq_name(
                sample=sample,
                lane=fastq['lane'],
                date=fastq['date'],
                flowcell=fastq['flowcell'],
                tile=fastq['tile'],
                read=fastq['read'],
                undetermined=fastq['undetermined'],
            )
            dest_path = root_dir / dest_name
            log.info(f"linking: {fastq['path']} -> {dest_path}")
            if not dry:
                os.link(fastq['path'], dest_path)
