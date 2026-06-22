# -*- coding: utf-8 -*-
"""ReYMeN_cli/providers.py — Provider CLI Komutlari.

LLM provider listeleme, degistirme ve test etme.
"""

from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def provider_list() -> str:
    """Kullanilabilir providerlari listele."""
    import sys
    sys.path.insert(0, str(PROJE_KOK))
    try:
        from providers import list_providers, mevcut_providerlar
        tumu = list_providers()
        mevcut = mevcut_providerlar()
        satirlar = [f"[Providers] Toplam {len(tumu)} provider:\n"]
        for p in tumu:
            durum = "MEVCUT" if p in mevcut else "ANAHTAR YOK"
            satirlar.append(f"  {p:<20} {durum}")
        return "\n".join(satirlar)
    except Exception as e:
        return f"[Providers] Yuklenemiyor: {e}"


def provider_test(ad: str) -> str:
    """Bir provider'i test et."""
    import sys
    sys.path.insert(0, str(PROJE_KOK))
    from providers import get_provider
    profil = get_provider(ad)
    if not profil:
        return f"[Providers] Bilinmeyen provider: {ad}"

    return f"[Providers] {profil.name}: {profil.base_url}, model={profil.default_model}"


def provider_switch(ad: str) -> str:
    """Varsayilan provider'i degistir."""
    import sys
    sys.path.insert(0, str(PROJE_KOK))
    from providers import get_provider
    profil = get_provider(ad)
    if not profil:
        return f"[Providers] Bilinmeyen provider: {ad}"

    # .env'yi guncelle
    env_yolu = PROJE_KOK / ".env"
    if env_yolu.exists():
        satirlar = env_yolu.read_text(encoding="utf-8").split("\n")
        yeni = []
        for satir in satirlar:
            if satir.startswith("ReYMeN_DEFAULT_PROVIDER="):
                yeni.append(f"ReYMeN_DEFAULT_PROVIDER={ad}")
            else:
                yeni.append(satir)
        env_yolu.write_text("\n".join(yeni), encoding="utf-8")
        return f"[Providers] Varsayilan provider: {ad}"

    return "[Providers] .env bulunamadi."


def provider_ping(ad: str) -> str:
    """Provider'a ping at."""
    import sys
    sys.path.insert(0, str(PROJE_KOK))
    import os
    from dotenv import load_dotenv
    load_dotenv(PROJE_KOK / ".env", override=True)
    from main import CONFIG
    from provider_transport import RuntimeProviderEngine
    prov = RuntimeProviderEngine(CONFIG)
    sonuc = prov.ping(ad)
    return f"[Providers] {ad}: {'CANLI' if sonuc else 'KAPALI'}"
