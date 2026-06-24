# -*- coding: utf-8 -*-
"""SHIM — agent/skill_bundles.py yönlendirir"""
from agent.skill_bundles import *  # noqa: F401, F403


def paket_listele() -> str:
    """Mevcut skill paketlerini listele."""
    try:
        from agent.skill_bundles import get_skill_bundles
        paketler = get_skill_bundles()
        if not paketler:
            return "Kayitli paket bulunamadi."
        return "\n".join(f"- {ad}" for ad in sorted(paketler.keys()))
    except Exception as e:
        return f"Paket listesi alinamadi: {e}"
