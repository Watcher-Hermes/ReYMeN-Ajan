# -*- coding: utf-8 -*-
"""ReYMeN_cli/security_advisories.py — Guvenlik Danismani CLI.

Guvenlik durumu kontrolu, danisma listeleme, oneriler, hizli tarama.
SECURITY.md dosyasini okur ve proje guvenlik durumunu degerlendirir.
"""

import json
import os
import stat
import sys
from datetime import datetime
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent
SECURITY_MD = PROJE_KOK / "SECURITY.md"
ADVISORY_DB = PROJE_KOK / ".ReYMeN" / "security" / "advisories.json"


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

    @classmethod
    def cyan(cls, metin: str) -> str:
        return cls.boya(metin, cls.CYAN)


def _advisory_oku() -> list:
    """Kayitli danismalari oku."""
    if not ADVISORY_DB.exists():
        return []
    try:
        with open(str(ADVISORY_DB), "r", encoding="utf-8") as f:
            icerik = f.read().strip()
            return json.loads(icerik) if icerik else []
    except (json.JSONDecodeError, Exception):
        return []


def _advisory_yaz(veri: list):
    """Danismalari dosyaya yaz."""
    ADVISORY_DB.parent.mkdir(parents=True, exist_ok=True)
    with open(str(ADVISORY_DB), "w", encoding="utf-8") as f:
        json.dump(veri, f, indent=2, ensure_ascii=False)


def guvenlik_durumu() -> str:
    """Projenin genel guvenlik durumunu kontrol et.

    .env dosyasi, .gitignore, SECURITY.md, izinler.

    Returns:
        str: Guvenlik durumu raporu
    """
    try:
        satirlar = [f"{Renk.mavi('[Guvenlik]')} Proje Guvenlik Durumu:\n"]
        sorun_sayisi = 0

        env_yol = PROJE_KOK / ".env"
        if env_yol.exists():
            satirlar.append(f"  {Renk.yesil('✓')} .env dosyasi mevcut")
            if sys.platform != "win32":
                mod = os.stat(str(env_yol)).st_mode
                if mod & stat.S_IROTH:
                    satirlar.append(f"  {Renk.sari('⚠')} .env baskalari tarafindan okunabilir")
                    sorun_sayisi += 1
        else:
            satirlar.append(f"  {Renk.sari('⚠')} .env dosyasi bulunamadi")
            sorun_sayisi += 1

        git_yol = PROJE_KOK / ".gitignore"
        if git_yol.exists():
            with open(str(git_yol), "r") as f:
                icerik = f.read()
            if ".env" in icerik:
                satirlar.append(f"  {Renk.yesil('✓')} .env .gitignore'da")
            else:
                satirlar.append(f"  {Renk.sari('⚠')} .env .gitignore'da degil")
                sorun_sayisi += 1
        else:
            satirlar.append(f"  {Renk.sari('⚠')} .gitignore bulunamadi")
            sorun_sayisi += 1

        if SECURITY_MD.exists():
            satirlar.append(f"  {Renk.yesil('✓')} SECURITY.md mevcut")
        else:
            satirlar.append(f"  {Renk.sari('⚠')} SECURITY.md bulunamadi")
            sorun_sayisi += 1

        ReYMeN_yol = PROJE_KOK / ".ReYMeN"
        if ReYMeN_yol.exists():
            satirlar.append(f"  {Renk.yesil('✓')} .ReYMeN/ dizini mevcut")
        else:
            satirlar.append(f"  {Renk.sari('⚠')} .ReYMeN/ dizini bulunamadi")
            sorun_sayisi += 1

        if sorun_sayisi == 0:
            satirlar.append(f"\n  {Renk.yesil('[GUVENLI]')} Tüm kontroller basarili.")
        else:
            satirlar.append(f"\n  {Renk.sari(f'[{sorun_sayisi} sorun]')} Duzeltme onerileri icin: guvenlik_oneri()")

        return "\n".join(satirlar)
    except Exception as e:
        return f"{Renk.kirmizi('[Guvenlik]')} Durum kontrolu hatasi: {e}"


def guvenlik_listele() -> str:
    """Bilinen guvenlik danismalarini listele."""
    try:
        danismalar = _advisory_oku()
        if not danismalar:
            return f"{Renk.sari('[Guvenlik]')} Kayitli danisma yok."

        satirlar = [f"{Renk.mavi(f'[Guvenlik] Danismalar ({len(danismalar)} adet):')}"]
        for d in danismalar:
            tarih = d.get("tarih", "???")
            seviye = d.get("seviye", "bilgi")
            seviye_renk = {
                "kritik": Renk.kirmizi("KRITIK"),
                "yuksek": Renk.sari("YUKSEK"),
                "orta": Renk.sari("ORTA"),
                "dusuk": Renk.cyan("DUSUK"),
            }.get(seviye, Renk.cyan(seviye.upper()))
            baslik = d.get("baslik", "Bilgi")
            satirlar.append(f"  [{tarih}] {seviye_renk} - {baslik}")
            if d.get("detay"):
                satirlar.append(f"    {d['detay']}")

        return "\n".join(satirlar)
    except Exception as e:
        return f"{Renk.kirmizi('[Guvenlik]')} Listeleme hatasi: {e}"


def guvenlik_oneri() -> str:
    """Guvenlik onerilerini goster.

    SECURITY.md okur ve proje yapisina gore oneriler sunar.

    Returns:
        str: Guvenlik oneri metni
    """
    try:
        satirlar = [f"{Renk.mavi('[Guvenlik]')} Guvenlik Onerileri:\n"]

        satirlar.append(f"  {Renk.kalin('Temel Onlemler:')}")
        satirlar.append(f"  {Renk.cyan('•')} .env dosyasini .gitignore'a ekleyin")
        satirlar.append(f"  {Renk.cyan('•')} .env dosyasina 600 izni verin (Unix)")
        satirlar.append(f"  {Renk.cyan('•')} API anahtarlarini sifreleyin (.ReYMeN/secrets/)")
        satirlar.append(f"  {Renk.cyan('•')} SECURITY.md dosyasini guncel tutun")
        satirlar.append(f"")

        if SECURITY_MD.exists():
            satirlar.append(f"  {Renk.kalin('SECURITY.md icerigi:')}")
            with open(str(SECURITY_MD), "r", encoding="utf-8") as f:
                for satir in f:
                    satir_stripped = satir.rstrip()
                    if satir_stripped:
                        satirlar.append(f"    {satir_stripped}")

        satirlar.append(f"")
        satirlar.append(f"  {Renk.kalin('Onerilen Ek Adimlar:')}")
        satirlar.append(f"  {Renk.cyan('•')} Haftalik guvenlik taramasi yapin (guvenlik_tara())")
        satirlar.append(f"  {Renk.cyan('•')} .ReYMeN/ dizinini yedekleyin")
        satirlar.append(f"  {Renk.cyan('•')} Pluginleri guvenilir kaynaklardan kurun")
        satirlar.append(f"  {Renk.cyan('•')} Hassas dosya yazma onayi kullanin (write_approval_commands)")

        return "\n".join(satirlar)
    except Exception as e:
        return f"{Renk.kirmizi('[Guvenlik]')} Oneri hatasi: {e}"


def guvenlik_tara() -> str:
    """Hizli guvenlik taramasi yap.

    Supheli icerik, hassas dosyalar ve .ReYMeN guvenligini kontrol eder.

    Returns:
        str: Tarama sonucu
    """
    try:
        satirlar = [f"{Renk.mavi('[Guvenlik]')} Hizli Guvenlik Taramasi:\n"]
        bulgu_sayisi = 0

        hassas_dosyalar = [".env", ".env.example", "credentials.json", "token.json", "config.json"]
        satirlar.append(f"  {Renk.kalin('1. Hassas Dosyalar:')}")
        for dosya in hassas_dosyalar:
            dosya_yol = PROJE_KOK / dosya
            if dosya_yol.exists():
                boyut = dosya_yol.stat().st_size
                satirlar.append(f"    {Renk.sari('⚠')} {dosya} ({boyut}B)")
                bulgu_sayisi += 1
        if bulgu_sayisi == 0:
            satirlar.append(f"    {Renk.yesil('✓')} Hassas dosya bulunamadi.")

        orta_kalip = ["exec(", "eval(", "os.system", "subprocess.call", "base64.b64decode"]
        py_dosyalari = list(PROJE_KOK.rglob("*.py"))
        satirlar.append(f"\n  {Renk.kalin('2. Supheli Kod:')}")
        supheli_sayisi = 0
        for py_dosya in py_dosyalari:
            try:
                with open(str(py_dosya), "r", encoding="utf-8") as f:
                    icerik = f.read()
                for kalip in orta_kalip:
                    if kalip in icerik:
                        rel_yol = py_dosya.relative_to(PROJE_KOK)
                        satirlar.append(f"    {Renk.sari('?')} {rel_yol}: {kalip}")
                        supheli_sayisi += 1
                        break
            except Exception:
                continue
        if supheli_sayisi == 0:
            satirlar.append(f"    {Renk.yesil('✓')} Supheli icerik bulunamadi.")
        else:
            bulgu_sayisi += supheli_sayisi

        satirlar.append(f"\n  {Renk.kalin('3. .ReYMeN Dizini:')}")
        ReYMeN_yol = PROJE_KOK / ".ReYMeN"
        if ReYMeN_yol.exists():
            ReYMeN_dosyalari = list(ReYMeN_yol.rglob("*"))
            satirlar.append(f"    {Renk.yesil('✓')} {len(ReYMeN_dosyalari)} dosya/dizin")
        else:
            satirlar.append(f"    {Renk.sari('⚠')} .ReYMeN dizini yok")
            bulgu_sayisi += 1

        ozet = f"\n  {Renk.kalin('Ozet:')} {bulgu_sayisi} bulgu"
        if bulgu_sayisi == 0:
            satirlar.append(f"  {Renk.yesil('[TEMIZ]')} Proje guvenli gorunuyor.")
        else:
            satirlar.append(f"  {Renk.sari(f'[ {bulgu_sayisi} BULGU ]')} Gozden gecirin: guvenlik_oneri()")
        satirlar.append(ozet)

        return "\n".join(satirlar)
    except Exception as e:
        return f"{Renk.kirmizi('[Guvenlik]')} Tarama hatasi: {e}"


def kaydet(alt_parser):
    """Security advisories CLI alt komutlarini argparse alt ayristiricisina kaydet.

    Alt komutlar: status, list, advice, scan
    """
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["status", "list", "advice", "scan"],
                            help="Islem (status|list|advice|scan)")


def calistir(args):
    """Security advisories komutunu calistir."""
    try:
        islem = args.islem or "status"

        if islem == "status":
            print(guvenlik_durumu())
        elif islem == "list":
            print(guvenlik_listele())
        elif islem == "advice":
            print(guvenlik_oneri())
        elif islem == "scan":
            print(guvenlik_tara())

    except Exception as e:
        print(f"{Renk.kirmizi('[Guvenlik]')} Komut hatasi: {e}")
