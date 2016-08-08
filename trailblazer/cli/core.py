# -*- coding: utf-8 -*-
from .base import build_cli
from trailblazer.store import Model

root = build_cli('analysis', Model=Model)
