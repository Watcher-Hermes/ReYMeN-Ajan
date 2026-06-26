# -*- coding: utf-8 -*-
"""providers.py — Sağlayıcı kayıt defteri (shim).

ReYMeN çok-sağlayıcılı LLM bağlantı katmanı için provider registry.
Beyin.py tarafından _guvensiz_import ile dinamik yüklenir.
"""

from __future__ import annotations

import os
from typing import Any, Optional


_PROVIDERS: dict[str, dict[str, Any]] = {
    "xiaomi": {
        "api_key": os.getenv("XIAOMI_API_KEY", ""),
        "base_url": "https://api.xiaomimimo.com/v1",
        "default_model": "mimo-v2.5-pro",
    },
    "deepseek": {
        "api_key": os.getenv("DEEPSEEK_API_KEY", ""),
        "base_url": "https://api.deepseek.com/v1",
        "default_model": "deepseek-v4-flash",
    },
    "groq": {
        "api_key": os.getenv("GROQ_API_KEY", ""),
        "base_url": "https://api.groq.com/openai/v1",
        "default_model": "deepseek-v4-flash",
    },
    "openai": {
        "api_key": os.getenv("OPENAI_API_KEY", ""),
        "base_url": "https://api.openai.com/v1",
        "default_model": "gpt-4o",
    },
    "lmstudio": {
        "api_key": "",
        "base_url": "http://localhost:1234/v1",
        "default_model": "local-model",
    },
    "ollama": {
        "api_key": "",
        "base_url": "http://localhost:11434/v1",
        "default_model": "llama3",
    },
}


def get_provider(ad: str) -> Optional[dict[str, Any]]:
    """Provider bilgilerini döndür.

    Args:
        ad: Provider adı (xiaomi, deepseek, groq, ...)

    Returns:
        dict veya None (bulunamazsa)
    """
    return _PROVIDERS.get(ad)


def list_providers() -> list[str]:
    """Tüm kayıtlı provider'ları listele."""
    return list(_PROVIDERS.keys())


def provider_ekle(ad: str, bilgi: dict[str, Any]) -> None:
    """Yeni provider ekle (runtime)."""
    _PROVIDERS[ad] = bilgi
