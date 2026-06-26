# -*- coding: utf-8 -*-
"""
md_denetim.py — Hizli .md dosyasi guncellik kontrolu (v2)

Sadece os.stat() + dosya boyutu ile calisir (icerik okumaz).
Günde 4 kez cron ile calistirilir.
"""

import json
import os
import time
from datetime import datetime
from pathlib import Path


def denetle(proje_koku: str = None) -> dict:
    if proje_koku is None:
        proje_koku = os.getcwd()

    kok = Path(proje_koku)
    simdi = time.time()

    rapor = {
        "tarih": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "toplam_md": 0,
        "skills_md": 0,
        "yeni_1s": 0,
        "orta_4s": 0,
        "eski_24s": 0,
        "cok_eski": 0,
        "bos_dosya": 0,
        "en_eski": "",
        "en_yeni": "",
        "en_eski_tarih": "",
        "en_yeni_tarih": "",
    }

    en_eski_zaman = simdi
    en_yeni_zaman = 0
    IGNORE_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv",
                   ".hermes", ".profile_backup", ".ReYMeN", "bot_venv"}

    for md_dosya in kok.rglob("*.md"):
        # Gizli/gereksiz klasörleri atla
        try:
            rel = md_dosya.relative_to(kok).parts
        except ValueError:
            continue
        if any(p.startswith(".") for p in rel):
            continue
        if any(p in IGNORE_DIRS for p in rel):
            continue

        rapor["toplam_md"] += 1
        if "skills" in rel:
            rapor["skills_md"] += 1

        try:
            mtime = md_dosya.stat().st_mtime
            boyut = md_dosya.stat().st_size
        except OSError:
            continue

        # Yaş kategorisi
        fark_saat = (simdi - mtime) / 3600
        if fark_saat < 1:
            rapor["yeni_1s"] += 1
        elif fark_saat < 4:
            rapor["orta_4s"] += 1
        elif fark_saat < 24:
            rapor["eski_24s"] += 1
        else:
            rapor["cok_eski"] += 1

        # Boş dosya (0 byte veya sadece ---)
        if boyut == 0:
            rapor["bos_dosya"] += 1
        elif boyut < 50:
            # Kucuk dosyalari icerikten kontrol et
            try:
                icerik = md_dosya.read_bytes()
                if icerik.strip() == b"" or icerik.strip() == b"---":
                    rapor["bos_dosya"] += 1
            except Exception:
                pass

        # En eski / en yeni
        if mtime < en_eski_zaman:
            en_eski_zaman = mtime
            rapor["en_eski"] = "/".join(rel)
            rapor["en_eski_tarih"] = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")
        if mtime > en_yeni_zaman:
            en_yeni_zaman = mtime
            rapor["en_yeni"] = "/".join(rel)
            rapor["en_yeni_tarih"] = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")

    return rapor


def rapor_olarak(r: dict) -> str:
    satir = []
    satir.append(f"📋 **MD Denetim Raporu** — {r['tarih']}")
    satir.append("")
    satir.append(f"| Metrik | Değer |")
    satir.append(f"|:-------|:------|")
    satir.append(f"| Toplam .md | {r['toplam_md']} |")
    satir.append(f"| Skills MD | {r['skills_md']} |")
    satir.append(f"| ✅ <1s | {r['yeni_1s']} |")
    satir.append(f"| ⚡ 1-4s | {r['orta_4s']} |")
    satir.append(f"| ⚠️ 4-24s | {r['eski_24s']} |")
    satir.append(f"| 🔴 >24s | {r['cok_eski']} |")
    satir.append(f"| 📄 Boş | {r['bos_dosya']} |")
    satir.append("")
    satir.append(f"**En yeni:** `{r['en_yeni']}` ({r['en_yeni_tarih']})")
    satir.append(f"**En eski:** `{r['en_eski']}` ({r['en_eski_tarih']})")
    satir.append("")

    sorunlar = []
    if r["cok_eski"] > 0:
        sorunlar.append(f"{r['cok_eski']} >24s")
    if r["bos_dosya"] > 0:
        sorunlar.append(f"{r['bos_dosya']} boş")
    if sorunlar:
        satir.append(f"⚠️ **Sorun:** {' + '.join(sorunlar)}")
    else:
        satir.append("✅ **Genel durum:** Temiz")
    return "\n".join(satir)


if __name__ == "__main__":
    import sys
    kok = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    r = denetle(kok)
    print(rapor_olarak(r))
    print("\n---JSON---")
    print(json.dumps(r, ensure_ascii=False))
