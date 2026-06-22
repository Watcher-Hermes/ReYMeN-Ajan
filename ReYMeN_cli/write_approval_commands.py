# -*- coding: utf-8 -*-
"""ReYMeN_cli/write_approval_commands.py — Yazma Onay Yonetimi CLI.

Hangi dosya yollarinin onay gerektirdigini yoneten kurallar.
Onay kurallari .ReYMeN/approval_rules.json dosyasinda saklanir.
"""

import json
import sys
from pathlib import Path
from fnmatch import fnmatch

PROJE_KOK = Path(__file__).parent.parent
ONAY_DOSYASI = PROJE_KOK / ".ReYMeN" / "approval_rules.json"


class Renk:
    """ReYMeN inline Renk — ANSI renk kodlari."""
    YESIL = "\033[92m"
    SARI = "\033[93m"
    KIRMIZI = "\033[91m"
    MAVI = "\033[94m"
    CYAN = "\033[96m"
    KALIN = "\033[1m"
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


def _onay_kurallari_oku() -> list:
    """Onay kurallarini oku."""
    if not ONAY_DOSYASI.exists():
        return []
    try:
        with open(str(ONAY_DOSYASI), "r", encoding="utf-8") as f:
            icerik = f.read().strip()
            return json.loads(icerik) if icerik else []
    except (json.JSONDecodeError, Exception):
        return []


def _onay_kurallari_yaz(kurallar: list):
    """Onay kurallarini dosyaya yaz."""
    ONAY_DOSYASI.parent.mkdir(parents=True, exist_ok=True)
    with open(str(ONAY_DOSYASI), "w", encoding="utf-8") as f:
        json.dump(kurallar, f, indent=2, ensure_ascii=False)


def yazma_onay_listele() -> str:
    """Mevcut yazma onay kurallarini listele.

    Returns:
        str: Kural listesi metni
    """
    try:
        kurallar = _onay_kurallari_oku()
        if not kurallar:
            return f"{Renk.sari('[Onay]')} Henuz onay kurali tanimlanmamis."

        satirlar = [f"{Renk.mavi(f'[Onay] Yazma Onay Kurallari ({len(kurallar)} adet):')}"]
        for i, kural in enumerate(kurallar, 1):
            desen = kural.get("desen", "???")
            aciklama = kural.get("aciklama", "")
            ek = f" — {aciklama}" if aciklama else ""
            satirlar.append(f"  {i}. {Renk.cyan(desen)}{ek}")

        return "\n".join(satirlar)
    except Exception as e:
        return f"{Renk.kirmizi('[Onay]')} Listeleme hatasi: {e}"


def yazma_onay_ekle(desen: str) -> str:
    """Yeni bir yazma onay kurali ekle.

    Args:
        desen: Dosya yolu deseni (ornek: *.env, config/*.json)

    Returns:
        str: Islem sonucu
    """
    try:
        if not desen or not desen.strip():
            return f"{Renk.sari('[Onay]')} Gecerli bir desen belirtin."

        desen = desen.strip()
        kurallar = _onay_kurallari_oku()

        if any(k.get("desen") == desen for k in kurallar):
            return f"{Renk.sari('[Onay]')} Bu desen zaten kayitli: {desen}"

        yeni_kural = {"desen": desen, "aciklama": ""}
        kurallar.append(yeni_kural)
        _onay_kurallari_yaz(kurallar)

        return f"{Renk.yesil('[Onay]')} Kural eklendi: {desen}"

    except Exception as e:
        return f"{Renk.kirmizi('[Onay]')} Ekleme hatasi: {e}"


def yazma_onay_kaldir(desen: str) -> str:
    """Bir yazma onay kuralini kaldir.

    Args:
        desen: Kaldirilacak desen (tam eslesme)

    Returns:
        str: Islem sonucu
    """
    try:
        if not desen or not desen.strip():
            return f"{Renk.sari('[Onay]')} Gecerli bir desen belirtin."

        desen = desen.strip()
        kurallar = _onay_kurallari_oku()
        yeni_kurallar = [k for k in kurallar if k.get("desen") != desen]

        if len(yeni_kurallar) == len(kurallar):
            return f"{Renk.sari('[Onay]')} Desen bulunamadi: {desen}"

        _onay_kurallari_yaz(yeni_kurallar)
        return f"{Renk.yesil('[Onay]')} Kural kaldirildi: {desen}"

    except Exception as e:
        return f"{Renk.kirmizi('[Onay]')} Kaldirma hatasi: {e}"


def yazma_onay_temizle() -> str:
    """Tum yazma onay kurallarini temizle.

    Returns:
        str: Islem sonucu
    """
    try:
        _onay_kurallari_yaz([])
        if ONAY_DOSYASI.exists():
            ONAY_DOSYASI.unlink()
            return f"{Renk.yesil('[Onay]')} Tum kurallar temizlendi."
        return f"{Renk.sari('[Onay]')} Zaten hic kural yok."
    except Exception as e:
        return f"{Renk.kirmizi('[Onay]')} Temizleme hatasi: {e}"


def onay_gerekli_mi(dosya_yolu: str) -> bool:
    """Bir dosya yolunun onay gerektirip gerekmedigini kontrol et.

    Desen eslestirmesi icin fnmatch kullanir.

    Args:
        dosya_yolu: Kontrol edilecek dosya yolu

    Returns:
        bool: Onay gerekiyorsa True
    """
    try:
        kurallar = _onay_kurallari_oku()
        for kural in kurallar:
            desen = kural.get("desen", "")
            if fnmatch(dosya_yolu, desen):
                return True
        return False
    except Exception:
        return False


def kaydet(alt_parser):
    """Write approval CLI alt komutlarini argparse alt ayristiricisina kaydet.

    Alt komutlar: list, add, remove, clear
    """
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["list", "add", "remove", "clear"],
                            help="Islem (list|add|remove|clear)")
    alt_parser.add_argument("--desen", type=str, default=None,
                            help="Dosya deseni (add/remove icin, orn: *.env)")


def calistir(args):
    """Write approval komutunu calistir."""
    try:
        islem = args.islem or "list"

        if islem == "list":
            print(yazma_onay_listele())

        elif islem == "add":
            if not args.desen:
                print(f"{Renk.sari('[Onay]')} Lutfen --desen belirtin (orn: *.env).")
                return
            print(yazma_onay_ekle(args.desen))

        elif islem == "remove":
            if not args.desen:
                print(f"{Renk.sari('[Onay]')} Lutfen --desen belirtin.")
                return
            print(yazma_onay_kaldir(args.desen))

        elif islem == "clear":
            print(yazma_onay_temizle())

    except Exception as e:
        print(f"{Renk.kirmizi('[Onay]')} Komut hatasi: {e}")
