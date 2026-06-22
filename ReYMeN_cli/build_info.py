# -*- coding: utf-8 -*-
"""ReYMeN_cli/build_info.py — Yapi bilgisi CLI.

Version, build, deps, hash, check islemleri.
"""

import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def _proje_versiyonu() -> str:
    """Proje versiyonunu oku."""
    init_yolu = PROJE_KOK / "__init__.py"
    if init_yolu.exists():
        with open(str(init_yolu), "r", encoding="utf-8") as f:
            for satir in f:
                if satir.startswith("__version__"):
                    return satir.split("=")[1].strip().strip('"').strip("'")
    return "0.1.0"


def _paket_versiyonu(paket: str) -> str:
    """Bir Python paketinin versiyonunu dondur."""
    try:
        mod = __import__(paket)
        if hasattr(mod, "__version__"):
            return mod.__version__
        return "?"
    except ImportError:
        return "Yok"


def kaydet(alt_parser):
    """Build info CLI alt komutlarini argparse alt ayristiricisina kaydet.

    Alt komutlar: version, build, deps, hash, check
    """
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["version", "build", "deps", "hash", "check"],
                            help="Yapilacak islem (version|build|deps|hash|check)")
    alt_parser.add_argument("--file", type=str, default=None,
                            help="Dosya yolu (hash icin)")
    alt_parser.add_argument("--output", type=str, default=None,
                            help="Cikti dosyasi (build icin)")


def calistir(args):
    """Build info komutunu calistir."""
    try:
        islem = args.islem or "version"

        if islem == "version":
            ver = _proje_versiyonu()
            print(f"[Build] Proje versiyonu: {ver}")
            print(f"[Build] Python: {sys.version}")
            print(f"[Build] Platform: {sys.platform}")

        elif islem == "build":
            ver = _proje_versiyonu()
            build_zamani = datetime.now().isoformat()
            build_bilgisi = {
                "versiyon": ver,
                "zaman": build_zamani,
                "python": sys.version,
                "platform": sys.platform,
            }
            output = args.output
            if output:
                with open(output, "w", encoding="utf-8") as f:
                    json.dump(build_bilgisi, f, indent=2, ensure_ascii=False)
                print(f"[Build] Yapi bilgisi kaydedildi: {output}")
            else:
                print(f"[Build] Yapi bilgisi:")
                for k, v in build_bilgisi.items():
                    print(f"  + {k}: {v}")

        elif islem == "deps":
            bagimliliklar = [
                ("Python", sys.version.split()[0]),
                ("typing", "hazir"),
            ]
            try:
                import flask
                bagimliliklar.append(("Flask", flask.__version__))
            except ImportError:
                bagimliliklar.append(("Flask", "Yok"))
            try:
                import requests
                bagimliliklar.append(("requests", requests.__version__))
            except ImportError:
                bagimliliklar.append(("requests", "Yok"))

            print(f"[Build] Bagimliliklar:")
            for ad, ver in bagimliliklar:
                print(f"  + {ad}: {ver}")

        elif islem == "hash":
            dosya = args.file
            if not dosya:
                print("[Build] Lutfen --file parametresini belirtin.")
                return
            dosya_yolu = Path(dosya)
            if not dosya_yolu.exists():
                print(f"[Build] Dosya bulunamadi: {dosya}")
                return
            with open(str(dosya_yolu), "rb") as f:
                icerik = f.read()
            md5 = hashlib.md5(icerik).hexdigest()
            sha1 = hashlib.sha1(icerik).hexdigest()
            sha256 = hashlib.sha256(icerik).hexdigest()
            print(f"[Build] Dosya: {dosya}")
            print(f"  MD5:    {md5}")
            print(f"  SHA1:   {sha1}")
            print(f"  SHA256: {sha256}")

        elif islem == "check":
            print(f"[Build] Proje kontrol ediliyor...")
            sorunlar = []
            gerekli_dosyalar = ["main.py", "setup.py", "motor.py", "beyin.py"]
            for d in gerekli_dosyalar:
                if not (PROJE_KOK / d).exists():
                    sorunlar.append(f"Eksik dosya: {d}")
            try:
                import flask
            except ImportError:
                sorunlar.append("Flask yuklu degil")
            if sorunlar:
                print(f"[Build] Sorunlar bulundu ({len(sorunlar)}):")
                for s in sorunlar:
                    print(f"  ! {s}")
            else:
                print("[Build] Her sey yolunda.")

    except Exception as e:
        print(f"[Build] Beklenmeyen hata: {e}")
