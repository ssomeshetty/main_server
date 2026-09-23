"""Compatibility package for the root-level Django project modules."""

import importlib
import sys

_apps = importlib.import_module('apps')
sys.modules.setdefault(__name__ + '.apps', _apps)
