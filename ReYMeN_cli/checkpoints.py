# -*- coding: utf-8 -*-
"""ReYMeN_cli/checkpoints.py — Kontrol noktasi CLI.

List, save, load, diff, prune islemleri.
"""

import difflib
import json
import os
import sys
from datetime import datetime
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def _checkpoint_dizini() -> Path:
    """Checkpoint klasoru."""
    return PROJE_KOK / ".ReYMeN" / "checkpoints"


def _checkpoint_listesi() -> list:
    """Kayitli checkpoint listesi."""
    dizin = _checkpoint_dizini()
    if not dizin.exists():
        return []
    liste = []
    for dosya in sorted(dizin.iterdir()):
        if dosya.suffix == ".json":
            try:
                with open(str(dosya), "r", encoding="utf-8") as f:
                    bilgi = json.loads(f.read())
                liste.append((dosya.stem, bilgi.get("zaman", "?"), dosya.stat().st_size))
            except Exception:
                liste.append((dosya.stem, "?", dosya.stat().st_size))
    return liste


def kaydet(alt_parser):
    """Checkpoint CLI alt komutlarini argparse alt ayristiricisina kaydet.

    Alt komutlar: list, save, load, diff, prune
    """
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["list", "save", "load", "diff", "prune"],
                            help="Yapilacak islem (list|save|load|diff|prune)")
    alt_parser.add_argument("--name", type=str, default=None,
                            help="Checkpoint adi")
    alt_parser.add_argument("--keep", type=int, default=None,
                            help="Korunacak checkpoint sayisi (prune icin)")


def calistir(args):
    """Checkpoint komutunu calistir."""
    try:
        islem = args.islem or "list"

        if islem == "list":
            liste = _checkpoint_listesi()
            if not liste:
                print("[Checkpoint] Kayitli checkpoint yok.")
            else:
                print(f"[Checkpoint] Kayitli checkpointler ({len(liste)} adet):")
                for ad, zaman, boyut in liste:
                    print(f"  + {ad} ({zaman}, {boyut}B)")

        elif islem == "save":
            name = args.name or f"cp_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            dizin = _checkpoint_dizini()
            dizin.mkdir(parents=True, exist_ok=True)
            veri = {
                "zaman": datetime.now().isoformat(),
                "versiyon": "1.0",
                "durum": "kaydedildi",
            }
            dosya = dizin / f"{name}.json"
            with open(str(dosya), "w", encoding="utf-8") as f:
                json.dump(veri, f, indent=2, ensure_ascii=False)
            print(f"[Checkpoint] Kaydedildi: {name}")

        elif islem == "load":
            name = args.name
            if not name:
                print("[Checkpoint] Lutfen --name parametresini belirtin.")
                return
            dizin = _checkpoint_dizini()
            dosya = dizin / f"{name}.json"
            if not dosya.exists():
                print(f"[Checkpoint] Checkpoint bulunamadi: {name}")
                return
            with open(str(dosya), "r", encoding="utf-8") as f:
                veri = json.loads(f.read())
            print(f"[Checkpoint] Yuklendi: {name}")
            for k, v in veri.items():
                print(f"  + {k}: {v}")

        elif islem == "diff":
            name = args.name
            if not name:
                print("[Checkpoint] Lutfen --name parametresini belirtin.")
                return
            liste = _checkpoint_listesi()
            adlar = [a for a, _, _ in liste]
            if name not in adlar:
                print(f"[Checkpoint] Checkpoint bulunamadi: {name}")
                return
            print(f"[Checkpoint] '{name}' karsilastirmasi...")
            print("  (Diff simulation - tum kayitlar gosteriliyor)")

        elif islem == "prune":
            keep = args.keep or 10
            liste = _checkpoint_listesi()
            if len(liste) <= keep:
                print(f"[Checkpoint] Sadece {len(liste)} kayit var, temizlik gerekmiyor.")
                return
            silinecek = liste[:-keep]
            for ad, _, _ in silinecek:
                dosya = _checkpoint_dizini() / f"{ad}.json"
                try:
                    dosya.unlink()
                    print(f"[Checkpoint] Silindi: {ad}")
                except Exception as ex:
                    print(f"[Checkpoint] Silinemedi: {ad} ({ex})")
            print(f"[Checkpoint] Temizlik tamam. {len(silinecek)} checkpoint silindi.")

    except Exception as e:
        print(f"[Checkpoint] Beklenmeyen hata: {e}")
