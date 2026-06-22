# -*- coding: utf-8 -*-
"""ReYMeN_cli/skills_config.py — Skill CLI Komutlari.

Skill yonetimi icin CLI komutlari.
"""

from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def skill_list(kategori: str = "", ayrintili: bool = False) -> str:
    """Skill'leri listele."""
    import sys
    sys.path.insert(0, str(PROJE_KOK))
    from skill_commands import listele
    return listele(kategori, ayrintili)


def skill_search(sorgu: str) -> str:
    """Skill icinde ara."""
    import sys
    sys.path.insert(0, str(PROJE_KOK))
    from skill_commands import ara
    return ara(sorgu)


def skill_add(kaynak: str) -> str:
    """Yeni skill ekle."""
    import sys
    sys.path.insert(0, str(PROJE_KOK))
    from skill_commands import ekle
    return ekle(kaynak)


def skill_remove(ad: str) -> str:
    """Skill sil."""
    import sys
    sys.path.insert(0, str(PROJE_KOK))
    from skill_commands import sil
    return sil(ad)


def skill_detail(ad: str) -> str:
    """Skill detayi goster."""
    import sys
    sys.path.insert(0, str(PROJE_KOK))
    from skill_commands import detay
    return detay(ad)


def skill_stats() -> str:
    """Skill istatistikleri."""
    import sys
    sys.path.insert(0, str(PROJE_KOK))
    from skill_commands import istatistik
    return istatistik()


def skill_bundle_create(kategori: str = "") -> str:
    """Skill paketi olustur."""
    import sys
    sys.path.insert(0, str(PROJE_KOK))
    from skill_bundles import paket_olustur
    return paket_olustur(kategori)


def skill_bundle_load(paket_yolu: str) -> str:
    """Skill paketi yukle."""
    import sys
    sys.path.insert(0, str(PROJE_KOK))
    from skill_bundles import paket_yukle
    return paket_yukle(paket_yolu)


def skill_hub_list() -> str:
    """Hub kaynaklarini listele."""
    import sys
    sys.path.insert(0, str(PROJE_KOK))
    from skills_hub import hub_listele
    return hub_listele()


def skill_hub_download(hub_adi: str, kategori: str = "") -> str:
    """Hub'dan skill indir."""
    import sys
    sys.path.insert(0, str(PROJE_KOK))
    from skills_hub import hub_indir
    return hub_indir(hub_adi, kategori)
