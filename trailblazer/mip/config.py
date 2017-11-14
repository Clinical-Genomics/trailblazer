# -*- coding: utf-8 -*-
from copy import deepcopy
import logging
from pathlib import Path

from marshmallow import Schema, fields, validate
import ruamel.yaml

from trailblazer.constants import DEFAULT_CAPTURE_KIT
from trailblazer.exc import ConfigError

LOG = logging.getLogger(__name__)


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
    capture_kit = fields.Str(default=DEFAULT_CAPTURE_KIT)


class ConfigSchema(Schema):
    family = fields.Str(required=True)
    default_gene_panels = fields.List(fields.Str(), required=True)
    samples = fields.List(fields.Nested(SampleSchema), required=True)


class ConfigHandler:

    def make_config(self, data: dict):
        """Make a MIP config."""
        self.validate_config(data)
        config_data = self.prepare_config(data)
        return config_data

    @staticmethod
    def validate_config(data: dict) -> dict:
        """Convert to MIP config format."""
        errors = ConfigSchema().validate(data)
        if errors:
            for field, messages in errors.items():
                if isinstance(messages, dict):
                    for level, sample_errors in messages.items():
                        sample_id = data['samples'][level]['sample_id']
                        for sub_field, sub_messages in sample_errors.items():
                            LOG.error(f"{sample_id} -> {sub_field}: {', '.join(sub_messages)}")
                else:
                    LOG.error(f"{field}: {', '.join(messages)}")
            raise ConfigError('invalid config input', errors=errors)

    @staticmethod
    def prepare_config(data: dict) -> dict:
        """Prepare the config data."""
        data_copy = deepcopy(data)
        # handle single sample cases with 'unknown' phenotype
        if len(data_copy['samples']) == 1:
            if data_copy['samples'][0]['phenotype'] == 'unknown':
                LOG.info("setting 'unknown' phenotype to 'unaffected'")
                data_copy['samples'][0]['phenotype'] = 'unaffected'
        # set the mother/father to '0' if they are not set for a sample
        for sample_data in data_copy['samples']:
            sample_data['mother'] = sample_data.get('mother') or '0'
            sample_data['father'] = sample_data.get('father') or '0'
            if sample_data['analysis_type'] == 'wgs' and sample_data.get('capture_kit') is None:
                sample_data['capture_kit'] = DEFAULT_CAPTURE_KIT
        return data_copy

    def save_config(self, data: dict) -> Path:
        """Save a config to the expected location."""
        out_dir = Path(self.families_dir) / data['family']
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / 'pedigree.yaml'
        dump = ruamel.yaml.round_trip_dump(data, indent=4, block_seq_indent=2)
        out_path.write_text(dump)
        return out_path
