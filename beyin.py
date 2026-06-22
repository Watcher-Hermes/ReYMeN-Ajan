# -*- coding: utf-8 -*-
# SHIM — reymen/cereyan/beyin.py yonlendirir
from reymen.cereyan.beyin import *  # noqa: F401, F403
from reymen.cereyan.beyin import _guvensiz_import  # noqa: F401 — test icin gerekli

# Private isimleri de disıaçar (testler için)
import importlib as _imp, sys as _sys
_src = _imp.import_module('reymen.cereyan.beyin')
_sys.modules[__name__].__dict__.update(
    {k: v for k, v in vars(_src).items() if k.startswith('_') and not k.startswith('__')}
)
