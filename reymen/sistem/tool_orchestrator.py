# -*- coding: utf-8 -*-
"""
tool_orchestrator.py — Araç yürütme orkestrasyonu.

motor.py'den ayrıştırıldı: Tool çağrısı akışını yönetir.
- Registry → Plugin → Fallback zincirini yürütür
- HITL kontrolü
- check_fn doğrulama
- Hook tetikleme
"""

import logging
from typing import Any, Optional, Dict, List, Tuple

log = logging.getLogger("motor.tool_orchestrator")


class ToolOrchestrator:
    """
    Araç çağrısı orkestratörü.

    3 katmanlı çözümleme zinciri:
    1. ToolRegistry (birincil)
    2. PluginManager (ikincil)
    3. Fallback (üçüncül)
    """

    def __init__(self, registry=None, plugin_mgr=None, fallback=None,
                 riskli_araclar=None, onay_fn=None, check_fns=None,
                 hooks=None):
        self._registry = registry
        self._plugin_mgr = plugin_mgr
        self._fallback = fallback
        self._riskli_araclar = riskli_araclar or frozenset()
        self._onay_fn = onay_fn
        self._check_fns = check_fns or {}
        self._hooks = hooks
        self._ekstra_izin_araclar: set = set()

    def calistir(self, arac: str, params: List[str]) -> str:
        """3 katmanlı çözümleme ile aracı çalıştır."""

        # 1. check_fn kontrolü
        _check = self._check_fns.get(arac)
        if _check is not None and not _check():
            log.warning(f"[Orch] {arac} check_fn engelledi")
            return f"[{arac}]: Bu araç bu ortamda kullanılamıyor."

        # 2. HITL: riskli araçlarda onay
        _izinli = arac in self._ekstra_izin_araclar
        if arac in self._riskli_araclar and not _izinli and self._onay_fn:
            ozet = (params[0] if params else "")[:120]
            if not self._onay_fn(arac, ozet):
                log.info(f"[Orch] {arac} HITL reddedildi")
                return f"[İptal]: Kullanıcı '{arac}' eylemini reddetti."

        # 3. ToolRegistry ile dene
        if self._registry:
            sonuc = self._registry.calistir(arac, *params)
            if not sonuc.startswith("[Bilinmeyen arac]"):
                self._hook_tetikle(arac, params, sonuc)
                return sonuc

        # 4. PluginManager ile dene
        if self._plugin_mgr:
            try:
                sonuc = self._plugin_mgr.run(arac.lower())
                self._hook_tetikle(arac, params, str(sonuc))
                return str(sonuc)
            except KeyError:
                pass

        # 5. Fallback
        if self._fallback:
            sonuc = self._fallback.calistir(arac, params)
        else:
            sonuc = f"[Hata]: Bilinmeyen araç: {arac}"

        self._hook_tetikle(arac, params, sonuc)
        return sonuc

    def _hook_tetikle(self, arac: str, params: List[str], sonuc: str):
        if self._hooks:
            self._hooks.tetikle("TOOL_CALLED", arac=arac, sonuc=sonuc)
