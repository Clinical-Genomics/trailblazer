import logging
from pathlib import Path

import click
import ruamel.yaml
from tabulate import tabulate

from trailblazer.mip import files

LOG = logging.getLogger(__name__)


@click.command()
@click.argument('family')
@click.pass_context
def check(context: click.Context, family: str):
    """Delete an analysis log from the database."""
    analysis_obj = context.obj['store'].analyses(family=family).first()
    if analysis_obj is None:
        LOG.error('no analysis found')
        context.abort()

    config_path = Path(analysis_obj.config_path)
    if not config_path.exists():
        LOG.error(f"analysis config not found: {config_path}")
        context.abort()
    config_raw = ruamel.yaml.safe_load(config_path.open())
    config_data = files.parse_config(config_raw)

    sampleinfo_raw = ruamel.yaml.safe_load(Path(config_data['sampleinfo_path']).open())
    sampleinfo_data = files.parse_sampleinfo(sampleinfo_raw)

    qcmetrics_path = Path(sampleinfo_data['qcmetrics_path'])
    if not qcmetrics_path.exists():
        LOG.error(f"qc metrics not found: {str(qcmetrics_path)}")
        context.abort()
    qcmetrics_raw = ruamel.yaml.safe_load(qcmetrics_path.open())
    qcmetrics_data = files.parse_qcmetrics(qcmetrics_raw)

    samples = {
        'sample': [],
        'type': [],
        'ped': [],
        'chanjo': [],
        'peddy': [],
        'plink': [],
        'duplicates': [],
    }
    for sample_data in config_data['samples']:
        LOG.debug(f"{sample_data['id']}: parse analysis config")
        samples['sample'].append(sample_data['id'])
        samples['type'].append(sample_data['type'])

    for sample_data in sampleinfo_data['samples']:
        LOG.debug(f"{sample_data['id']}: parse sample info")
        samples['ped'].append(sample_data['sex'])

        with Path(sample_data['chanjo_sexcheck']).open() as chanjo_handle:
            sexcheck_data = files.parse_chanjo_sexcheck(chanjo_handle)

        predicted_sex = sexcheck_data['predicted_sex']
        xy_ratio = sexcheck_data['y_coverage'] / sexcheck_data['x_coverage']
        samples['chanjo'].append(f"{predicted_sex} ({xy_ratio:.3f})")

    for sample_data in qcmetrics_data['samples']:
        LOG.debug(f"{sample_data['id']}: parse qc metrics")
        samples['plink'].append(sample_data['plink_sex'])
        duplicates_percent = sample_data['duplicates'] * 100
        samples['duplicates'].append(f"{duplicates_percent:.3f}%")

    peddy_path = Path(sampleinfo_data['peddy']['sex_check'])
    if peddy_path.exists():
        with peddy_path.open() as sexcheck_handle:
            peddy_data = files.parse_peddy_sexcheck(sexcheck_handle)

        for sample_id in samples['sample']:
            LOG.debug(f"{sample_id}: parse peddy")
            predicted_sex = peddy_data[sample_id]['predicted_sex']
            het_ratio = peddy_data[sample_id]['het_ratio']
            samples['peddy'].append(f"{predicted_sex} ({het_ratio})")
    else:
        LOG.warning(f"missing peddy output: {peddy_path}")

    print(tabulate(samples, headers='keys', tablefmt='psql'))
