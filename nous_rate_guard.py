# -*- coding: utf-8 -*-
"""SHIM — agent/nous_rate_guard.py yönlendirir + ReYMeN API uyum katmanı.

beyin.py şu üç fonksiyonu kullanır:
  rate_guard_izin_ver(provider) -> bool   — istek yapılabilir mi?
  rate_guard_basla(provider)              — istek başlamadan çağrılır
  rate_guard_bitir(provider)              — istek bittikten sonra çağrılır

Hermes API'si (agent/nous_rate_guard.py):
  nous_rate_limit_remaining() -> float|None
  record_nous_rate_limit(...)
  clear_nous_rate_limit()
"""
from agent.nous_rate_guard import *  # noqa: F401, F403
from agent.nous_rate_guard import nous_rate_limit_remaining  # explicit

# Private name export — test patching için
import importlib as _imp_nrg, sys as _sys_nrg
_src_nrg = _imp_nrg.import_module('agent.nous_rate_guard')
_sys_nrg.modules[__name__].__dict__.update(
    {k: v for k, v in vars(_src_nrg).items() if k.startswith('_') and not k.startswith('__')}
)

import threading as _threading
import time as _time

_kilit = _threading.Lock()
_aktif_istekler: dict = {}  # provider → başlangıç zamanı


def rate_guard_izin_ver(provider: str) -> bool:
    """True → istek yapılabilir, False → hız sınırı aktif (atla)."""
    kalan = nous_rate_limit_remaining()
    return kalan is None  # None = rate limit yok


def rate_guard_basla(provider: str) -> None:
    """İstek başlamadan önce başlangıç zamanını kaydet."""
    with _kilit:
        _aktif_istekler[provider] = _time.monotonic()


def rate_guard_bitir(provider: str) -> None:
    """İstek bittikten sonra kaydı temizle."""
    with _kilit:
        _aktif_istekler.pop(provider, None)


class RateGuard:
    """Basit hız sınırı + eş zamanlı istek sınırlayıcı."""

    def __init__(self, max_per_second: float = 10.0, max_concurrent: int = 5):
        self._max_per_second = max_per_second
        self._max_concurrent = max_concurrent
        self._kilit = _threading.Lock()
        self._aktif: dict = {}
        self._son_istek: float = 0.0

    def izin_ver(self, provider: str) -> bool:
        with self._kilit:
            simdi = _time.monotonic()
            aralik = 1.0 / self._max_per_second if self._max_per_second > 0 else 0
            if simdi - self._son_istek < aralik:
                return False
            if len(self._aktif) >= self._max_concurrent:
                return False
            return True

    def istek_basla(self, provider: str) -> None:
        with self._kilit:
            self._aktif[provider] = _time.monotonic()
            self._son_istek = _time.monotonic()

    def istek_bitir(self, provider: str) -> None:
        with self._kilit:
            self._aktif.pop(provider, None)
