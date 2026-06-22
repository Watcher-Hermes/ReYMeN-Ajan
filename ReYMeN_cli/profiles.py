# -*- coding: utf-8 -*-
"""ReYMeN_cli/profiles.py — Profil CLI Komutlari.

ReYMeN profilleri arasinda gecis ve yonetim.
"""

from pathlib import Path

PROFIL_KLASOR = Path(__file__).parent.parent / ".ReYMeN" / "profiles"
PROFIL_KLASOR.mkdir(parents=True, exist_ok=True)


def _get_default_ReYMeN_home() -> Path:
    """ReYMeN ana dizinini döndür — __init__ vs. için kullanılır.

    Returns:
        Path: ~/.ReYMeN dizini (veya ReYMeN_HOME env override'ı)
    """
    import os
    override = os.environ.get("ReYMeN_HOME")
    if override:
        return Path(override)
    return Path.home() / ".ReYMeN"


def profile_list() -> str:
    """Mevcut profilleri listele."""
    profiller = [d.name for d in PROFIL_KLASOR.iterdir() if d.is_dir()]
    if not profiller:
        return "[Profiles] Henuz profil yok. (varsayilan: default)"

    satirlar = ["[Profiles]"]
    for p in profiller:
        satirlar.append(f"  - {p}")
    return "\n".join(satirlar)


def profile_create(ad: str) -> str:
    """Yeni profil olustur."""
    profil_yolu = PROFIL_KLASOR / ad
    if profil_yolu.exists():
        return f"[Profiles] Zaten var: {ad}"
    profil_yolu.mkdir(parents=True)
    (profil_yolu / "MEMORY.md").write_text(f"# {ad} Profili\n", encoding="utf-8")
    (profil_yolu / "USER.md").write_text(f"# {ad} Kullanici\n", encoding="utf-8")
    return f"[Profiles] Olusturuldu: {ad}"


def profile_switch(ad: str) -> str:
    """Profile gecis yap (.env'yi guncelle)."""
    env_yolu = Path(__file__).parent.parent / ".env"
    if not env_yolu.exists():
        return "[Profiles] .env bulunamadi."

    satirlar = env_yolu.read_text(encoding="utf-8").split("\n")
    yeni = []
    for satir in satirlar:
        if satir.startswith("ReYMeN_PROFILE="):
            yeni.append(f"ReYMeN_PROFILE={ad}")
        else:
            yeni.append(satir)
    env_yolu.write_text("\n".join(yeni), encoding="utf-8")
    return f"[Profiles] Gecis yapildi: {ad}"


def profile_current() -> str:
    """Mevcut profili goster."""
    import os
    mevcut = os.environ.get("ReYMeN_PROFILE", "default")
    return f"[Profiles] Mevcut: {mevcut}"
