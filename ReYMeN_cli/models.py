# -*- coding: utf-8 -*-
"""ReYMeN_cli/models.py — Model CLI Komutlari.

Model listeleme, kiyaslama ve benchmark.
"""

from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def model_list(provider: str = "") -> str:
    """Modelleri listele."""
    import sys
    sys.path.insert(0, str(PROJE_KOK))
    from model_metadata import model_listele
    modeller = model_listele(provider)
    if not modeller:
        return "[Models] Model bulunamadi."
    satirlar = [f"[Models] {len(modeller)} model:\n"]
    for m in modeller:
        satirlar.append(f"  {m['ad']:<30} {m['provider']:<10} {m['context']}ctx  ${m['fiyat']}/M")
    return "\n".join(satirlar)


def model_detail(ad: str) -> str:
    """Model detayi goster."""
    import sys
    sys.path.insert(0, str(PROJE_KOK))
    from model_metadata import model_bilgisi
    bilgi = model_bilgisi(ad)
    if not bilgi:
        return f"[Models] Bilinmiyor: {ad}"
    return (
        f"[Models] {ad}\n"
        f"  Provider: {bilgi.get('provider', '?')}\n"
        f"  Context: {bilgi.get('context', '?')} token\n"
        f"  Fiyat: ${bilgi.get('fiyat', '?')}/M token\n"
        f"  Vision: {bilgi.get('vision', False)}\n"
        f"  Hiz: {bilgi.get('hiz', '?')}"
    )


def model_recommend(istek: str) -> str:
    """Ihtiyaca gore model oner."""
    import sys
    sys.path.insert(0, str(PROJE_KOK))
    from model_metadata import modele_gore_sec
    modeller = modele_gore_sec(istek)
    if not modeller:
        return "[Models] Uygun model bulunamadi."
    return "[Models] Onerilen:\n" + "\n".join(f"  - {m}" for m in modeller)


def model_benchmark(modeller: list[str] = None) -> str:
    """Model benchmark testi."""
    import sys
    sys.path.insert(0, str(PROJE_KOK))
    import os
    from dotenv import load_dotenv
    load_dotenv(PROJE_KOK / ".env", override=True)
    from main import CONFIG
    from provider_transport import RuntimeProviderEngine
    prov = RuntimeProviderEngine(CONFIG)
    from model_tools import benchmark_calistir, benchmark_raporu

    if not modeller:
        from models_dev import BENCHMARK_MODELS
        modeller = BENCHMARK_MODELS

    print(f"[Benchmark] {len(modeller)} model test ediliyor...")
    sonuclar = benchmark_calistir(prov, modeller)
    return benchmark_raporu(sonuclar)
