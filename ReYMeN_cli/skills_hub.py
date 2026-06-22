# -*- coding: utf-8 -*-
"""ReYMeN_cli/skills_hub.py — Skill Hub Yonetimi CLI.

Skill merkezi (hub) uzerinden skill listeleme, arama,
indirme, yukleme ve paylasma islemleri.
ReYMeN'in kendi skills/ klasoru ile calisir,
GitHub/ReYMeN-skills reposu uzerinden skill getirir.
"""

import json
import os
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Optional


class Renk:
    """ReYMeN Renk sinifi — skills_hub ciktisi icin."""
    YESIL = "\033[92m"
    SARI = "\033[93m"
    KIRMIZI = "\033[91m"
    MAVI = "\033[94m"
    CYAN = "\033[96m"
    MOR = "\033[95m"
    KALIN = "\033[1m"
    SOLUK = "\033[2m"
    SON = "\033[0m"

    @classmethod
    def boya(cls, metin: str, kod: str) -> str:
        return f"{kod}{metin}{cls.SON}"

    @classmethod
    def yesil(cls, metin: str) -> str:
        return cls.boya(metin, cls.YESIL)

    @classmethod
    def sari(cls, metin: str) -> str:
        return cls.boya(metin, cls.SARI)

    @classmethod
    def kirmizi(cls, metin: str) -> str:
        return cls.boya(metin, cls.KIRMIZI)

    @classmethod
    def mavi(cls, metin: str) -> str:
        return cls.boya(metin, cls.MAVI)

    @classmethod
    def cyan(cls, metin: str) -> str:
        return cls.boya(metin, cls.CYAN)

    @classmethod
    def mor(cls, metin: str) -> str:
        return cls.boya(metin, cls.MOR)

    @classmethod
    def kalin(cls, metin: str) -> str:
        return cls.boya(metin, cls.KALIN)


PROJE_KOK = Path(__file__).parent.parent
SKILLS_KLASOR = PROJE_KOK / ".ReYMeN" / "skills"
HUB_CACHE = SKILLS_KLASOR / "index-cache" / "hub"

# Varsayilan hub kaynaklari
HUBS = {
    "ReYMeN-skills": {
        "url": "https://github.com/Watcher-Hermes/ReYMeN-skills/archive/refs/heads/main.zip",
        "aciklama": "ReYMeN ana skill reposu (Watcher-Hermes/ReYMeN-skills)",
    },
    "ReYMeN-agent-skills": {
        "url": "https://github.com/nousresearch/ReYMeN-agent-skills/archive/refs/heads/main.zip",
        "aciklama": "Nous Research ReYMeN Agent skill havuzu",
    },
    "ReYMeN-community": {
        "url": "https://github.com/nousresearch/ReYMeN-agent-skills/archive/refs/heads/main.zip",
        "aciklama": "ReYMeN topluluk skill havuzu (community)",
    },
}


def _skill_sayisi() -> int:
    """Skills klasorundeki SKILL.md sayisini dondur."""
    try:
        if not SKILLS_KLASOR.exists():
            return 0
        return len(list(SKILLS_KLASOR.rglob("SKILL.md")))
    except Exception:
        return 0


def hub_listele(kaynak: str = "github") -> str:
    """Kullanilabilir hub kaynaklarini listele.

    Args:
        kaynak: Kaynak turu (github/local).

    Returns:
        str: Renkli hub listesi.
    """
    try:
        satirlar = [
            f"{Renk.kalin('[Skills Hub] Kullanilabilir kaynaklar')}",
        ]

        if kaynak == "github":
            for ad, bilgi in HUBS.items():
                satirlar.append(
                    f"  {Renk.cyan('📦')} {Renk.kalin(ad)}\n"
                    f"    {bilgi['aciklama']}\n"
                    f"    URL: {bilgi['url'][:70]}..."
                )
        else:
            # Yerel skills klasorunu tara
            if SKILLS_KLASOR.exists():
                for skill_dizini in sorted(SKILLS_KLASOR.iterdir()):
                    if skill_dizini.is_dir():
                        skill_md = skill_dizini / "SKILL.md"
                        aciklama = ""
                        if skill_md.exists():
                            try:
                                with open(str(skill_md), "r", encoding="utf-8") as f:
                                    ilk_satir = f.readline().strip()
                                    aciklama = f" - {ilk_satir[:60]}"
                            except Exception:
                                pass
                        satirlar.append(
                            f"  {Renk.yesil('📄')} {skill_dizini.name}{aciklama}"
                        )
            else:
                satirlar.append(f"  {Renk.sari('Skills klasoru bulunamadi.')}")

        satirlar.append(f"\n  {Renk.soluk(f'Toplam {_skill_sayisi()} skill yuklu.')}")
        return "\n".join(satirlar)
    except Exception as e:
        return f"{Renk.kirmizi('[Hub]')} Listeleme hatasi: {e}"


def hub_ara(sorgu: str) -> str:
    """Hub'da skill ara.

    Args:
        sorgu: Aranacak metin.

    Returns:
        str: Arama sonuclari.
    """
    try:
        if not sorgu or not sorgu.strip():
            return f"{Renk.sari('[Hub]')} Arama sorgusu gerekli."

        sorgu_kucuk = sorgu.lower().strip()
        sonuclar = []

        # Hub isimlerinde ara
        for ad, bilgi in HUBS.items():
            if sorgu_kucuk in ad.lower() or sorgu_kucuk in bilgi["aciklama"].lower():
                sonuclar.append(("hub", ad, bilgi["aciklama"]))

        # Yerel skill'lerde ara
        if SKILLS_KLASOR.exists():
            for skill_dizini in SKILLS_KLASOR.iterdir():
                if skill_dizini.is_dir() and sorgu_kucuk in skill_dizini.name.lower():
                    sonuclar.append(("yerel", skill_dizini.name, ""))
                else:
                    skill_md = skill_dizini / "SKILL.md"
                    if skill_md.exists():
                        try:
                            icerik = skill_md.read_text(encoding="utf-8")
                            if sorgu_kucuk in icerik.lower():
                                sonuclar.append(("yerel", skill_dizini.name, icerik[:80]))
                        except Exception:
                            pass

        if not sonuclar:
            return f"{Renk.sari('[Hub]')} '{sorgu}' icin sonuc bulunamadi."

        satirlar = [Renk.kalin(f"[Hub] '{sorgu}' icin {len(sonuclar)} sonuc:")]
        for tip, ad, detay in sonuclar:
            ikon = "📦" if tip == "hub" else "📄"
            renk = Renk.cyan if tip == "hub" else Renk.yesil
            satirlar.append(f"  {ikon} {renk(ad)} [{tip}]")
            if detay:
                satirlar.append(f"     {detay[:70]}")

        return "\n".join(satirlar)
    except Exception as e:
        return f"{Renk.kirmizi('[Hub]')} Arama hatasi: {e}"


def hub_indir(skill_adi: str, hedef_klasor: str = ".ReYMeN/skills") -> str:
    """Hub'dan skill indir ve yukle.

    Args:
        skill_adi: Indirilecek skill adi.
        hedef_klasor: Hedef klasor (varsayilan: .ReYMeN/skills).

    Returns:
        str: Islem sonucu.
    """
    try:
        hedef = Path(hedef_klasor)
        if not hedef.is_absolute():
            hedef = PROJE_KOK / hedef_klasor

        hedef.mkdir(parents=True, exist_ok=True)

        # Skill'i hub'larda ara
        for hub_adi, hub_bilgi in HUBS.items():
            try:
                import requests
                print(f"{Renk.cyan('[Hub]')} {hub_adi}'den indiriliyor: {skill_adi}...")

                r = requests.get(hub_bilgi["url"], timeout=60)
                if r.status_code != 200:
                    continue

                HUB_CACHE.mkdir(parents=True, exist_ok=True)
                zip_yolu = HUB_CACHE / f"{hub_adi}.zip"
                zip_yolu.write_bytes(r.content)

                with tempfile.TemporaryDirectory() as tmpdir:
                    with zipfile.ZipFile(zip_yolu, "r") as zf:
                        zf.extractall(tmpdir)

                    tmp_path = Path(tmpdir)
                    kok = next((d for d in tmp_path.iterdir() if d.is_dir()), None)
                    if not kok:
                        continue

                    skills_kaynak = kok / "skills"
                    if not skills_kaynak.exists():
                        continue

                    # Skill'i bul ve kopyala
                    for skill_dizini in skills_kaynak.iterdir():
                        if skill_dizini.is_dir() and skill_dizini.name == skill_adi:
                            skill_hedef = hedef / skill_dizini.name
                            if skill_hedef.exists():
                                shutil.rmtree(str(skill_hedef))
                            shutil.copytree(str(skill_dizini), str(skill_hedef))
                            return (
                                f"{Renk.yesil('[Hub]')} '{skill_adi}' basariyla "
                                f"indirildi -> {skill_hedef}"
                            )

                    # Tum skill'leri listele
                    mevcut = [d.name for d in skills_kaynak.iterdir() if d.is_dir()]
                    if mevcut:
                        return (
                            f"{Renk.sari('[Hub]')} '{skill_adi}' bulunamadi. "
                            f"Mevcut skill'ler: {', '.join(mevcut[:10])}"
                        )

            except ImportError:
                return f"{Renk.kirmizi('[Hub]')} 'requests' kutuphanesi gerekli."

        return f"{Renk.kirmizi('[Hub]')} '{skill_adi}' hicbir hub'da bulunamadi."
    except Exception as e:
        return f"{Renk.kirmizi('[Hub]')} Indirme hatasi: {e}"


def hub_yukle(kaynak_url: str) -> str:
    """URL'den skill yukle.

    Args:
        kaynak_url: Skill ZIP URL'si veya yerel dosya yolu.

    Returns:
        str: Islem sonucu.
    """
    try:
        kaynak = Path(kaynak_url)
        if kaynak.exists() and kaynak.suffix == ".zip":
            # Yerel ZIP dosyasi
            with tempfile.TemporaryDirectory() as tmpdir:
                with zipfile.ZipFile(str(kaynak), "r") as zf:
                    zf.extractall(tmpdir)

                tmp_path = Path(tmpdir)
                SKILLS_KLASOR.mkdir(parents=True, exist_ok=True)
                once = _skill_sayisi()

                for dizin in tmp_path.iterdir():
                    if dizin.is_dir():
                        hedef = SKILLS_KLASOR / dizin.name
                        if hedef.exists():
                            shutil.rmtree(str(hedef))
                        shutil.copytree(str(dizin), str(hedef))

                sonra = _skill_sayisi()
                yeni = sonra - once
                return f"{Renk.yesil('[Hub]')} Yukleme tamam: {yeni} yeni skill (toplam {sonra})"
        else:
            # URL'den indir
            import requests
            print(f"{Renk.cyan('[Hub]')} URL'den indiriliyor: {kaynak_url}")

            r = requests.get(kaynak_url, timeout=120)
            if r.status_code != 200:
                return f"{Renk.kirmizi('[Hub]')} HTTP {r.status_code}"

            HUB_CACHE.mkdir(parents=True, exist_ok=True)
            zip_yolu = HUB_CACHE / f"remote_{abs(hash(kaynak_url))}.zip"
            zip_yolu.write_bytes(r.content)

            return hub_yukle(str(zip_yolu))

        return f"{Renk.sari('[Hub]')} Desteklenmeyen kaynak."
    except ImportError:
        return f"{Renk.kirmizi('[Hub]')} 'requests' kutuphanesi gerekli."
    except Exception as e:
        return f"{Renk.kirmizi('[Hub]')} Yukleme hatasi: {e}"


def hub_paylas(skill_adi: str) -> str:
    """Skill'i paylasmak icin disa aktar (ZIP).

    Args:
        skill_adi: Paylasilacak skill adi.

    Returns:
        str: Islem sonucu.
    """
    try:
        skill_dizini = SKILLS_KLASOR / skill_adi
        if not skill_dizini.exists() or not skill_dizini.is_dir():
            return f"{Renk.kirmizi('[Hub]')} Skill bulunamadi: {skill_adi}"

        # Skill meta bilgisi
        skill_md = skill_dizini / "SKILL.md"
        aciklama = ""
        if skill_md.exists():
            try:
                aciklama = skill_md.read_text(encoding="utf-8").split("\n")[0][:60]
            except Exception:
                pass

        # ZIP olarak paketle
        exports_dir = PROJE_KOK / "exports"
        exports_dir.mkdir(exist_ok=True)
        zip_adi = f"skill_{skill_adi}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        zip_yolu = exports_dir / zip_adi

        shutil.make_archive(
            str(zip_yolu.with_suffix("")), "zip", str(skill_dizini)
        )

        boyut = zip_yolu.stat().st_size
        satirlar = [
            f"{Renk.yesil('[Hub]')} Skill paylasima hazir:",
            f"  Ad: {Renk.kalin(skill_adi)}",
            f"  Aciklama: {aciklama or 'Aciklama yok'}",
            f"  Dosya: {zip_yolu}",
            f"  Boyut: {boyut} B ({boyut / 1024:.1f} KB)",
            f"  {Renk.cyan('Paylasmak icin bu ZIP dosyasini gonderebilirsiniz.')}",
        ]
        return "\n".join(satirlar)
    except Exception as e:
        return f"{Renk.kirmizi('[Hub]')} Paylasma hatasi: {e}"


from datetime import datetime
