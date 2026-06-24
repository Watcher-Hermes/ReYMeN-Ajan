# -*- coding: utf-8 -*-
# SHIM + standalone — tools/execute_code_tool.py yönlendirir
from reymen.arac.execute_code_tool import *  # noqa: F401, F403
from reymen.arac.execute_code_tool import _guvenlik_kontrol  # noqa: F401, F403


def run(kod: str = "", timeout: int = 30, zaman_asimi=None, calisma_dizini: str = "") -> str:
    """Shim wrapper — [Hata] for empty code, accepts zaman_asimi alias."""
    if not kod or not kod.strip():
        return "[Hata]: kod parametresi bos olamaz."
    # zaman_asimi, timeout'un Türkçe karşılığı
    if zaman_asimi is not None:
        try:
            timeout = int(zaman_asimi)
        except (ValueError, TypeError):
            pass  # gecersiz deger — varsayilan kullan
    from tools.execute_code_tool import run as _inner_run
    try:
        return _inner_run(kod, timeout=timeout, calisma_dizini=calisma_dizini)
    except Exception as e:
        return f"[Hata]: {e}"
