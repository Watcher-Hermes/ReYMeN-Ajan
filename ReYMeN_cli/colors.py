# -*- coding: utf-8 -*-
"""ReYMeN_cli/colors.py — Renk temasi CLI.

List, set, preview, reset, export islemleri.
"""

import json
import os
import sys
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def _tema_dosyasi() -> Path:
    """Tema konfigurasyon dosyasi."""
    return PROJE_KOK / ".ReYMeN" / "colors" / "tema.json"


def _tema_oku() -> dict:
    """Mevcut temayi oku."""
    dosya = _tema_dosyasi()
    if not dosya.exists():
        return {"renkler": {}, "aktif_tema": "varsayilan"}
    try:
        with open(str(dosya), "r", encoding="utf-8") as f:
            icerik = f.read().strip()
            return json.loads(icerik) if icerik else {"renkler": {}, "aktif_tema": "varsayilan"}
    except (json.JSONDecodeError, Exception):
        return {"renkler": {}, "aktif_tema": "varsayilan"}


def _tema_yaz(veri: dict):
    """Temayi dosyaya yaz."""
    dosya = _tema_dosyasi()
    dosya.parent.mkdir(parents=True, exist_ok=True)
    with open(str(dosya), "w", encoding="utf-8") as f:
        json.dump(veri, f, indent=2, ensure_ascii=False)


def kaydet(alt_parser):
    """Colors CLI alt komutlarini argparse alt ayristiricisina kaydet.

    Alt komutlar: list, set, preview, reset, export
    """
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["list", "set", "preview", "reset", "export"],
                            help="Yapilacak islem (list|set|preview|reset|export)")
    alt_parser.add_argument("--name", type=str, default=None,
                            help="Tema adi (set icin)")
    alt_parser.add_argument("--key", type=str, default=None,
                            help="Renk anahtari (set icin)")
    alt_parser.add_argument("--value", type=str, default=None,
                            help="Renk degeri (set icin)")
    alt_parser.add_argument("--output", type=str, default=None,
                            help="Cikti dosyasi (export icin)")


def calistir(args):
    """Colors komutunu calistir."""
    try:
        islem = args.islem or "list"

        if islem == "list":
            tema = _tema_oku()
            print(f"[Colors] Aktif tema: {tema.get('aktif_tema', 'varsayilan')}")
            renkler = tema.get("renkler", {})
            if not renkler:
                print("[Colors] Ozel renk tanimi yok.")
            else:
                print(f"[Colors] Tanimli renkler ({len(renkler)} adet):")
                for k, v in renkler.items():
                    print(f"  + {k}: {v}")

        elif islem == "set":
            tema = _tema_oku()
            name = args.name
            key = args.key
            value = args.value
            if name:
                tema["aktif_tema"] = name
                _tema_yaz(tema)
                print(f"[Colors] Aktif tema degistirildi: {name}")
            elif key and value:
                if "renkler" not in tema:
                    tema["renkler"] = {}
                tema["renkler"][key] = value
                _tema_yaz(tema)
                print(f"[Colors] Renk ayarlandi: {key} = {value}")
            else:
                print("[Colors] Lutfen --name veya --key/--value parametrelerini belirtin.")

        elif islem == "preview":
            tema = _tema_oku()
            print(f"[Colors] Tema onizleme ({tema.get('aktif_tema', 'varsayilan')}):")
            renkler = tema.get("renkler", {})
            if not renkler:
                print("  (Varsayilan renkler kullaniliyor)")
            for k, v in renkler.items():
                print(f"  [{k}: {v}]")

        elif islem == "reset":
            tema = _tema_oku()
            tema["renkler"] = {}
            tema["aktif_tema"] = "varsayilan"
            _tema_yaz(tema)
            print("[Colors] Tema varsayilana sifirlandi.")

        elif islem == "export":
            tema = _tema_oku()
            output = args.output
            if output:
                with open(output, "w", encoding="utf-8") as f:
                    json.dump(tema, f, indent=2, ensure_ascii=False)
                print(f"[Colors] Tema export edildi: {output}")
            else:
                print(json.dumps(tema, indent=2, ensure_ascii=False))

    except Exception as e:
        print(f"[Colors] Beklenmeyen hata: {e}")
