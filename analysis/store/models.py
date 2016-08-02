# -*- coding: utf-8 -*-
from datetime import datetime
import json

import alchy
from sqlalchemy import Column, types


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, datetime):
        serial = obj.isoformat()
        return serial
    raise TypeError('Type not serializable')


class JsonModel(alchy.ModelBase):

    def to_json(self, pretty=False):
        """Serialize Model to JSON."""
        kwargs = dict(indent=4, sort_keys=True) if pretty else dict()
        return json.dumps(self.to_dict(), default=json_serial, **kwargs)


Model = alchy.make_declarative_base(Base=JsonModel)


class Analysis(Model):

    """Analysis record."""

    id = Column(types.Integer, primary_key=True)
    name = Column(types.String(128), unique=True)

    # metadata
    pipeline = Column(types.Enum('mip'))
    pipeline_version = Column(types.String(32))
    started_at = Column(types.DateTime)
    completed_at = Column(types.DateTime)
    status = Column(types.Enum('running', 'completed', 'errored'))
    root_dir = Column(types.String(128), unique=True)
    type = Column(types.Enum('exomes', 'genomes'))
    failed_step = Column(types.String(128))
