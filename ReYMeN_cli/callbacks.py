# -*- coding: utf-8 -*-
"""ReYMeN_cli/callbacks.py — Callback yonetimi CLI.

List, add, remove, test, log islemleri.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def _callback_dosyasi() -> Path:
    """Callback kayit dosyasi."""
    return PROJE_KOK / ".ReYMeN" / "callbacks" / "callbacks.json"


def _callbackleri_oku() -> dict:
    """Kayitli callbackleri oku."""
    dosya = _callback_dosyasi()
    if not dosya.exists():
        return {}
    try:
        with open(str(dosya), "r", encoding="utf-8") as f:
            icerik = f.read().strip()
            return json.loads(icerik) if icerik else {}
    except (json.JSONDecodeError, Exception):
        return {}


def _callbackleri_yaz(callbackler: dict):
    """Callbackleri dosyaya yaz."""
    dosya = _callback_dosyasi()
    dosya.parent.mkdir(parents=True, exist_ok=True)
    with open(str(dosya), "w", encoding="utf-8") as f:
        json.dump(callbackler, f, indent=2, ensure_ascii=False)


def prompt_for_secret(cli_ref, var_name: str, prompt: str, metadata=None) -> dict:
    """Prompt the user interactively for a secret value.

    Returns dict with 'value' key containing the secret.
    """
    try:
        from prompt_toolkit.shortcuts import input_dialog
        from prompt_toolkit.shortcuts import message_dialog
    except ImportError:
        print(f"[Secret] {prompt}")
        val = input(f"[Secret] {var_name}: ")
        return {"value": val}
    try:
        result = input_dialog(
            title=f"Secret: {var_name}",
            text=prompt,
            password=True,
        ).run()
        if result is None:
            return {"value": None, "cancelled": True}
        return {"value": result}
    except Exception:
        print(f"[Secret] {prompt}")
        val = input(f"[Secret] {var_name}: ")
        return {"value": val}


def kaydet(alt_parser):
    """Callback CLI alt komutlarini argparse alt ayristiricisina kaydet.

    Alt komutlar: list, add, remove, test, log
    """
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["list", "add", "remove", "test", "log"],
                            help="Yapilacak islem (list|add|remove|test|log)")
    alt_parser.add_argument("--name", type=str, default=None,
                            help="Callback adi")
    alt_parser.add_argument("--url", type=str, default=None,
                            help="Callback URL (add icin)")
    alt_parser.add_argument("--event", type=str, default=None,
                            help="Tetiklenecek olay")


def calistir(args):
    """Callback komutunu calistir."""
    try:
        islem = args.islem or "list"

        if islem == "list":
            callbackler = _callbackleri_oku()
            if not callbackler:
                print("[Callback] Kayitli callback yok.")
            else:
                print(f"[Callback] Kayitli callbackler ({len(callbackler)} adet):")
                for ad, bilgi in sorted(callbackler.items()):
                    url = bilgi.get("url", "?")
                    olay = bilgi.get("event", "?")
                    print(f"  + {ad}: {olay} -> {url}")

        elif islem == "add":
            name = args.name
            url = args.url
            event = args.event
            if not name or not url:
                print("[Callback] Lutfen --name ve --url parametrelerini belirtin.")
                return
            callbackler = _callbackleri_oku()
            callbackler[name] = {
                "url": url,
                "event": event or "all",
                "olusturma": datetime.now().isoformat(),
            }
            _callbackleri_yaz(callbackler)
            print(f"[Callback] Callback eklendi: {name}")

        elif islem == "remove":
            name = args.name
            if not name:
                print("[Callback] Lutfen --name parametresini belirtin.")
                return
            callbackler = _callbackleri_oku()
            if name not in callbackler:
                print(f"[Callback] Callback bulunamadi: {name}")
                return
            del callbackler[name]
            _callbackleri_yaz(callbackler)
            print(f"[Callback] Callback silindi: {name}")

        elif islem == "test":
            name = args.name
            if not name:
                print("[Callback] Lutfen --name parametresini belirtin.")
                return
            callbackler = _callbackleri_oku()
            if name not in callbackler:
                print(f"[Callback] Callback bulunamadi: {name}")
                return
            bilgi = callbackler[name]
            print(f"[Callback] Test ediliyor: {name} -> {bilgi.get('url')}")
            try:
                import urllib.request
                veri = json.dumps({"test": True, "zaman": datetime.now().isoformat()}).encode()
                req = urllib.request.Request(bilgi["url"], data=veri,
                                             headers={"Content-Type": "application/json"})
                urllib.request.urlopen(req, timeout=5)
                print(f"[Callback] Test basarili.")
            except Exception as ex:
                print(f"[Callback] Test basarisiz: {ex}")

        elif islem == "log":
            print(f"[Callback] Callback loglari gosteriliyor...")
            log_yolu = PROJE_KOK / ".ReYMeN" / "callbacks" / "log.json"
            if log_yolu.exists():
                with open(str(log_yolu), "r", encoding="utf-8") as f:
                    icerik = f.read().strip()
                    if icerik:
                        loglar = json.loads(icerik)
                        for kayit in loglar[-10:]:
                            print(f"  {kayit}")
                    else:
                        print("[Callback] Henuz log yok.")
            else:
                print("[Callback] Henuz log yok.")

    except Exception as e:
        print(f"[Callback] Beklenmeyen hata: {e}")
