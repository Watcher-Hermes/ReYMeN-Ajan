"""motor/context.py — Context compression, prompt caching, PII temizlik."""
import json
import os
import datetime as _dt
from typing import Optional

from reymen.cereyan.motor.config import _GATEWAY_STATE_PATH

try:
    from context_compressor import ContextCompressor
    _COMPRESSOR = ContextCompressor(max_token=4096)
except ImportError:
    _COMPRESSOR = None

try:
    from prompt_caching import PromptCache
    _CACHE = PromptCache(max_boyut=100, ttl_saniye=3600)
except ImportError:
    _CACHE = None

try:
    from agent.redact import redact_sensitive_text as _agent_temizle
except ImportError:
    _agent_temizle = None
try:
    from redact import tam_temizle as _pii_temizle
except ImportError:
    _pii_temizle = lambda m: m


def cevabi_temizle(cevap: str) -> str:
    if not cevap:
        return cevap
    if _agent_temizle:
        cevap = _agent_temizle(cevap)
    if callable(_pii_temizle):
        cevap = _pii_temizle(cevap)
    return cevap


def context_sikistir(gecmis: list) -> list:
    if _COMPRESSOR and len(gecmis) > 15:
        return _COMPRESSOR.sikistir(gecmis)
    return gecmis


def cache_kontrol(prompt: str, sistem: str = "") -> Optional[str]:
    if _CACHE:
        return _CACHE.al(sistem, [{"role": "user", "content": prompt}])
    return None


def cache_kaydet(prompt: str, yanit: str, sistem: str = "") -> None:
    if _CACHE:
        _CACHE.ekle(sistem, [{"role": "user", "content": prompt}], yanit)


def gateway_durum_yaz(state: str = "running", hata: str = "") -> None:
    try:
        payload = {
            "pid": os.getpid(),
            "kind": "reymen-gateway",
            "gateway_state": state,
            "active_agents": 0,
            "platforms": {
                "telegram": {
                    "state": "connected" if state == "running" else "disconnected",
                    "error_code": None,
                    "error_message": hata or None,
                    "updated_at": _dt.datetime.now().isoformat(),
                }
            },
            "updated_at": _dt.datetime.now().isoformat(),
        }
        _GATEWAY_STATE_PATH.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
        )
    except Exception as e:
        import logging
        logging.getLogger("motor").debug("Gateway state yazilamadi: %s", e)
