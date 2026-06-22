# -*- coding: utf-8 -*-
# SHIM — reymen/cereyan/conversation_loop.py yonlendirir
from reymen.cereyan.conversation_loop import *  # noqa: F401, F403
from reymen.cereyan.conversation_loop import motor_tools_schema_al, _motor_tools_schema_al  # noqa: F401
import re as _re

# ── ReYMeN ek API'leri ───────────────────────────────────────────────────────

GOREV_BITTI_TETIK = [
    "GOREV_BITTI",
    "GÖREV_BİTTİ",
    "TASK_COMPLETE",
    "TASK_DONE",
    "görev bitti",
    "tamamlandi",
]

_EYLEM_RE = _re.compile(r"Eylem:\s*(\w+)\s*\(([^)]*)\)", _re.IGNORECASE)
_ARAC_RE  = _re.compile(r"(\w+)\(([^)]*)\)")


class _Budget:
    """Tur bütçesi yöneticisi."""
    def __init__(self, max_tur: int = 15):
        self.max_tur = max_tur
        self._tur = 0
        self.kaldi = max_tur

    def adim_at(self) -> bool:
        if self._tur >= self.max_tur:
            return False
        self._tur += 1
        self.kaldi = self.max_tur - self._tur
        return True


_COMPRESSOR = None
_CACHE: dict = {}
