# -*- coding: utf-8 -*-
# SHIM — reymen/cereyan/motor.py yonlendirir
from reymen.cereyan.motor import *  # noqa: F401, F403

# Private isimleri de disari aktar (testler icin gerekli)
import importlib as _imp, sys as _sys
_src = _imp.import_module('reymen.cereyan.motor')
_sys.modules[__name__].__dict__.update(
    {k: v for k, v in vars(_src).items() if k.startswith('_') and not k.startswith('__')}
)
