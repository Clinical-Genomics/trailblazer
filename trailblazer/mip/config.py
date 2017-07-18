# -*- coding: utf-8 -*-
from copy import deepcopy
import logging
from pathlib import Path

from marshmallow import Schema, fields, validate
import ruamel.yaml

log = logging.getLogger(__name__)


class SampleSchema(Schema):
    sample_id = fields.Str(required=True)
    analysis_type = fields.Str(
        required=True,
        validate=validate.OneOf(choices=['wes', 'wgs', 'tga'])
    )
    father = fields.Str(default='0')
    mother = fields.Str(default='0')
    phenotype = fields.Str(
        required=True,
        validate=validate.OneOf(choices=['affected', 'unaffected', 'unknown'])
    )
    sex = fields.Str(
        required=True,
        validate=validate.OneOf(choices=['male', 'female', 'unknown'])
    )
    expected_coverage = fields.Float()
    capture_kit = fields.Str(
        validate=validate.OneOf(choices=['Agilent_SureSelectCRE.V1',
                                         'Agilent_SureSelect.V5',
                                         'Agilent_SureSelectFocusedExome.V1']),
        default='Agilent_SureSelectCRE.V1'
    )


class ConfigSchema(Schema):
    family = fields.List(fields.Str(), required=True)
    default_gene_panels = fields.List(fields.Str(), required=True)
    samples = fields.List(fields.Nested(SampleSchema), required=True)


class ConfigHandler:

    def validate(data: dict) -> dict:
        """Convert to MIP config format."""
        errors = ConfigSchema.validate(data)
        if errors:
            return errors

    def prepare(data: dict) -> dict:
        """Prepare the config data."""
        data_copy = deepcopy(data)
        # handle single sample cases with 'unknown' phenotype
        if len(data['samples']) == 1:
            if data['samples'][0]['phenotype'] == 'unknown':
                log.info("setting 'unknown' phenotype to 'unaffected'")
                data_copy['samples'][0]['phenotype'] = 'unaffected'
        return data_copy

    def save(root_dir: str, data: dict) -> Path:
        """Save a config to the expected location."""
        out_path = Path(root_dir) / 'pedigree.yaml'
        dump = ruamel.yaml.safe_dump(data)
        out_path.write_text(dump)
        return out_path
