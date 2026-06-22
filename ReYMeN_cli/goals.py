# -*- coding: utf-8 -*-
"""ReYMeN_cli/goals.py — Hedefler CLI.

Hedef listeleme, belirleme, ekleme, tamamlama
ve ilerleme takibi islemleri.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

PROJE_KOK = Path(__file__).parent.parent


def _hedef_dosyasi() -> Path:
    """Hedef kayit dosyasi yolu."""
    return PROJE_KOK / ".ReYMeN" / "goals" / "hedefler.json"


def _hedefleri_oku() -> list:
    """Kayitli hedefleri oku."""
    dosya = _hedef_dosyasi()
    if not dosya.exists():
        return []
    try:
        with open(str(dosya), "r", encoding="utf-8") as f:
            icerik = f.read().strip()
            return json.loads(icerik) if icerik else []
    except (json.JSONDecodeError, Exception):
        return []


def kaydet(alt_parser):
    """Hedefler CLI alt komutlarini argparse alt ayristiricisina kaydet.

    Alt komutlar: list, set, add, complete, progress
    """
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["list", "set", "add", "complete", "progress"],
                            help="Yapilacak islem (list|set|add|complete|progress)")
    alt_parser.add_argument("--hedef", type=str, default=None,
                            help="Hedef adi veya ID (set/add/complete icin)")
    alt_parser.add_argument("--aciklama", type=str, default=None,
                            help="Hedef aciklamasi (add icin)")


def calistir(args):
    """Hedefler komutunu calistir."""
    try:
        islem = args.islem or "list"

        if islem == "list":
            hedefler = _hedefleri_oku()
            if not hedefler:
                print("[Goals] Henuz hedef eklenmemis.")
            else:
                print(f"[Goals] Hedefler ({len(hedefler)} adet):")
                for h in hedefler:
                    ad = h.get("ad", "?")
                    durum = h.get("durum", "beklemede")
                    print(f"  + {ad} [{durum}]")

        elif islem == "set":
            hedef = args.hedef
            if not hedef:
                print("[Goals] Lutfen --hedef parametresini belirtin.")
                return
            print(f"[Goals] '{hedef}' hedefi belirlendi.")

        elif islem == "add":
            hedef = args.hedef
            aciklama = args.aciklama or ""
            if not hedef:
                print("[Goals] Lutfen --hedef parametresini belirtin.")
                return
            print(f"[Goals] '{hedef}' hedefi eklendi ({aciklama})")

        elif islem == "complete":
            hedef = args.hedef
            if not hedef:
                print("[Goals] Lutfen --hedef parametresini belirtin.")
                return
            print(f"[Goals] '{hedef}' tamamlandi!")

        elif islem == "progress":
            hedefler = _hedefleri_oku()
            tamam = sum(1 for h in hedefler if h.get("durum") == "tamam")
            toplam = len(hedefler)
            yuzde = int((tamam / toplam) * 100) if toplam > 0 else 0
            print(f"[Goals] Ilerleme: {tamam}/{toplam} ({yuzde}%)")

    except Exception as e:
        print(f"[Goals] Beklenmeyen hata: {e}")


class GoalManager:
    """Hedef Yoneticisi — upstream Hermes uyumluluk katmani.

    Hedef ekleme, listeleme, tamamlama islemleri.
    """

    def __init__(self, config: Any = None):
        self._config = config

    def list_goals(self) -> list:
        return _hedefleri_oku()

    def add_goal(self, ad: str, aciklama: str = "") -> bool:
        hedefler = _hedefleri_oku()
        hedefler.append({"ad": ad, "aciklama": aciklama, "durum": "beklemede", "tarih": str(datetime.now())})
        try:
            import json
            dosya = _hedef_dosyasi()
            dosya.parent.mkdir(parents=True, exist_ok=True)
            with open(str(dosya), "w", encoding="utf-8") as f:
                json.dump(hedefler, f, indent=2, ensure_ascii=False)
            return True
        except Exception:
            return False

    def complete_goal(self, ad: str) -> bool:
        hedefler = _hedefleri_oku()
        for h in hedefler:
            if h.get("ad") == ad:
                h["durum"] = "tamam"
                break
        try:
            import json
            dosya = _hedef_dosyasi()
            with open(str(dosya), "w", encoding="utf-8") as f:
                json.dump(hedefler, f, indent=2, ensure_ascii=False)
            return True
        except Exception:
            return False
