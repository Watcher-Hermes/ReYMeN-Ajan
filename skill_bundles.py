# -*- coding: utf-8 -*-
"""SHIM — agent/skill_bundles.py yönlendirir"""
from agent.skill_bundles import *  # noqa: F401, F403


def paket_listele() -> str:
    """Skill paketlerini listele."""
    from agent.skill_bundles import scan_bundles
    try:
        paketler = scan_bundles()
        if not paketler:
            return "[Paket] Paket bulunamadi."
        satirlar = [f"[Paket] {len(paketler)} paket:"]
        for ad in sorted(paketler):
            satirlar.append(f"  - {ad}")
        return "\n".join(satirlar)
    except Exception as e:
        return f"[Paket] Listelenemedi: {e}"
