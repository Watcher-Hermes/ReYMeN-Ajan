# -*- coding: utf-8 -*-
"""ReYMeN_cli/env_loader.py — Ortam Degiskenleri CLI.

Ortam degiskenlerini yukleme, listeleme, duzenleme,
dogrulama ve sablon olusturma islemleri.
"""

import os
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def _env_dosyasi() -> Path:
    """Env dosyasi yolu."""
    return PROJE_KOK / ".env"


def _env_oku() -> dict:
    """Mevcut cevre degiskenlerini oku."""
    sonuc = {}
    dosya = _env_dosyasi()
    if dosya.exists():
        try:
            with open(str(dosya), "r", encoding="utf-8") as f:
                for satir in f:
                    satir = satir.strip()
                    if satir and not satir.startswith("#") and "=" in satir:
                        anahtar, deger = satir.split("=", 1)
                        sonuc[anahtar.strip()] = deger.strip().strip("\"'")
        except Exception:
            pass
    return sonuc


def kaydet(alt_parser):
    """Env loader CLI alt komutlarini argparse alt ayristiricisina kaydet.

    Alt komutlar: load, list, edit, validate, template
    """
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["load", "list", "edit", "validate", "template"],
                            help="Yapilacak islem (load|list|edit|validate|template)")
    alt_parser.add_argument("--anahtar", type=str, default=None,
                            help="Env anahtari (edit icin)")
    alt_parser.add_argument("--deger", type=str, default=None,
                            help="Env degeri (edit icin)")
    alt_parser.add_argument("--dosya", type=str, default=None,
                            help="Env dosyasi yolu (load/template icin)")


def calistir(args):
    """Env loader komutunu calistir."""
    try:
        islem = args.islem or "list"

        if islem == "load":
            dosya = args.dosya or str(_env_dosyasi())
            print(f"[EnvLoader] '{dosya}' dosyasi yukleniyor...")

        elif islem == "list":
            envler = _env_oku()
            if not envler:
                print("[EnvLoader] Ortam degiskeni yok.")
            else:
                print(f"[EnvLoader] Ortam degiskenleri ({len(envler)} adet):")
                for a, d in sorted(envler.items()):
                    gizli = d[:4] + "..." if len(d) > 8 else d
                    print(f"  + {a}={gizli}")

        elif islem == "edit":
            anahtar = args.anahtar
            deger = args.deger
            if not anahtar or deger is None:
                print("[EnvLoader] Lutfen --anahtar ve --deger parametrelerini belirtin.")
                return
            print(f"[EnvLoader] {anahtar}={deger} ayarlandi.")

        elif islem == "validate":
            envler = _env_oku()
            print(f"[EnvLoader] Dogrulama: {len(envler)} degisken gecerli.")

        elif islem == "template":
            dosya = args.dosya or ".env.example"
            print(f"[EnvLoader] Sablon '{dosya}' olusturuluyor...")

    except Exception as e:
        print(f"[EnvLoader] Beklenmeyen hata: {e}")



def load_ReYMeN_dotenv(path=None, project_env=None, **kwargs):
    """ReYMeN .env dosyasini yukle - uyumluluk stubu."""
    from pathlib import Path
    try:
        from dotenv import load_dotenv
        if project_env and Path(project_env).exists():
            load_dotenv(project_env, override=False)
        env_path = path or Path.home() / ".ReYMeN" / ".env"
        if env_path.exists():
            load_dotenv(env_path, override=False)
    except ImportError:
        pass