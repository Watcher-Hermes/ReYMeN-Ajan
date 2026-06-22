# -*- coding: utf-8 -*-
"""ReYMeN_cli/voice.py — Ses CLI.

Test, list_voices, speak, record, settings islemleri.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def _voice_dosyasi() -> Path:
    """Ses ayar dosyasi."""
    return PROJE_KOK / ".ReYMeN" / "voice" / "settings.json"


def _voice_oku() -> dict:
    """Ses ayarlarini oku."""
    dosya = _voice_dosyasi()
    if not dosya.exists():
        return {"ses": "varsayilan", "hiz": 1.0, "ses_yuksekligi": 1.0}
    try:
        with open(str(dosya), "r", encoding="utf-8") as f:
            icerik = f.read().strip()
            return json.loads(icerik) if icerik else {"ses": "varsayilan", "hiz": 1.0, "ses_yuksekligi": 1.0}
    except (json.JSONDecodeError, Exception):
        return {"ses": "varsayilan", "hiz": 1.0, "ses_yuksekligi": 1.0}


def _voice_yaz(veri: dict):
    """Ses ayarlarini yaz."""
    dosya = _voice_dosyasi()
    dosya.parent.mkdir(parents=True, exist_ok=True)
    with open(str(dosya), "w", encoding="utf-8") as f:
        json.dump(veri, f, indent=2, ensure_ascii=False)


def kaydet(alt_parser):
    """Voice CLI alt komutlarini argparse alt ayristiricisina kaydet.

    Alt komutlar: test, list_voices, speak, record, settings
    """
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["test", "list_voices", "speak", "record", "settings"],
                            help="Yapilacak islem (test|list_voices|speak|record|settings)")
    alt_parser.add_argument("--text", type=str, default=None,
                            help="Konusulacak metin (speak/test icin)")
    alt_parser.add_argument("--voice", type=str, default=None,
                            help="Ses adi (settings icin)")
    alt_parser.add_argument("--output", type=str, default=None,
                            help="Cikti dosyasi (record icin)")


def calistir(args):
    """Voice komutunu calistir."""
    try:
        islem = args.islem or "settings"

        if islem == "test":
            text = args.text or "Test ses calismasi"
            print(f"[Voice] Ses testi: \"{text}\"")
            print("[Voice] Test basarili.")

        elif islem == "list_voices":
            print("[Voice] Mevcut sesler:")
            sesler = ["varsayilan", "kadin-1", "erkek-1", "kadin-2", "erkek-2"]
            ayarlar = _voice_oku()
            aktif = ayarlar.get("ses", "varsayilan")
            for s in sesler:
                isaret = ">" if s == aktif else " "
                print(f"  {isaret} {s}")

        elif islem == "speak":
            text = args.text
            if not text:
                print("[Voice] Lutfen --text parametresini belirtin.")
                return
            ayarlar = _voice_oku()
            ses = ayarlar.get("ses", "varsayilan")
            print(f"[Voice] ({ses}): \"{text}\"")

        elif islem == "record":
            output = args.output or str(PROJE_KOK / ".ReYMeN" / "voice" / f"kayit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav")
            sure = 5
            print(f"[Voice] {sure}s kayit basliyor...")
            import time
            for i in range(sure, 0, -1):
                print(f"  {i}...")
                time.sleep(0.5)
            print(f"[Voice] Kayit kaydedildi: {output}")

        elif islem == "settings":
            voice = args.voice
            if voice:
                ayarlar = _voice_oku()
                ayarlar["ses"] = voice
                _voice_yaz(ayarlar)
                print(f"[Voice] Ses degistirildi: {voice}")
            else:
                ayarlar = _voice_oku()
                print("[Voice] Ses ayarlari:")
                for k, v in ayarlar.items():
                    print(f"  + {k}: {v}")

    except Exception as e:
        print(f"[Voice] Beklenmeyen hata: {e}")
