# -*- coding: utf-8 -*-
"""motor.py — Eski public API shim (modüler yapıya yönlendirir).

Yeni yapı: motor/ klasörü altında config.py, providers.py, plugins.py,
context.py, main.py.

Kullanım (değişmedi):
    from reymen.cereyan.motor import Motor
    m = Motor()
    m.calistir("DOSYA_OKU", '"test.txt"')
"""
from reymen.cereyan.motor import Motor, provider_degistir

__all__ = ["Motor", "provider_degistir"]
