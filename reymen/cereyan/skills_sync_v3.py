#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
skills_sync_v3.py — Tek seferlik düzeltme + sync
"""
import sqlite3, hashlib
from datetime import date, timedelta
from pathlib import Path

DB = Path("reymen/cereyan/.ReYMeN/ogrenmeler.db")
SKILLS_DIR = Path("reymen/cereyan/skills")
ROOT = Path("reymen/cereyan")

def baglan():
    con = sqlite3.connect(str(DB), timeout=30)
    con.execute("PRAGMA busy_timeout=30000")
    return con

def main():
    con = baglan()

    # 1. Önce yanlış formattaki kayıtları temizle
    cur = con.execute(
        "SELECT COUNT(*) FROM ogrenmeler "
        "WHERE kaynak_url IS NOT NULL AND kaynak_url LIKE 'skills/%' AND kaynak_url NOT LIKE 'file://%'"
    )
    wrong = cur.fetchone()[0]
    print(f"Yanlis format kayit: {wrong}")

    cur = con.execute("SELECT COUNT(*) FROM ogrenmeler")
    toplam_once = cur.fetchone()[0]
    print(f"TOPLAM once: {toplam_once}")

    if wrong > 0:
        cur = con.execute(
            "DELETE FROM ogrenmeler "
            "WHERE kaynak_url IS NOT NULL AND kaynak_url LIKE 'skills/%' AND kaynak_url NOT LIKE 'file://%'"
        )
        deleted = con.total_changes
        con.commit()
        print(f"Silinen mukerrer: {deleted}")
        cur = con.execute("SELECT COUNT(*) FROM ogrenmeler")
        print(f"TOPLAM sonra: {cur.fetchone()[0]}")
    else:
        deleted = 0
        print("Temizlik gerekmiyor (0 yanlis format)")

    # 2. Mevcut DB'deki skills kayıtlarını indeksle
    cur = con.execute(
        "SELECT kaynak_url FROM ogrenmeler WHERE kategori LIKE 'skills%' AND kaynak_url IS NOT NULL"
    )
    existing = set()
    for row in cur.fetchall():
        kurl = str(row[0])
        # file:// ön ekini kaldır
        if kurl.startswith("file://"):
            kurl = kurl[7:]
        # Tüm backslashları forward slash yap
        kurl = kurl.replace("\\", "/")
        # skills/ kısmını bul
        idx = kurl.lower().find("skills/")
        if idx >= 0:
            normalized = kurl[idx:]
            existing.add(normalized)

    print(f"DB'de essiz skills kaydi: {len(existing)}")

    # 3. Dizindeki tüm .md dosyalarını tara
    md_files = sorted(SKILLS_DIR.rglob("*.md"))
    print(f"Toplam .md dosyasi: {len(md_files)}")

    yeni = 0
    guncel = 0
    bugun = date.today().isoformat()
    gec = (date.today() + timedelta(days=180)).isoformat()
    degisti_ama_guncellenmedi = 0

    for fp in md_files:
        try:
            rel = fp.relative_to(ROOT).as_posix()  # skills/Skiller/...
        except ValueError:
            rel = str(fp.relative_to(ROOT.parent).as_posix())
            if "reymen/cereyan/" in rel:
                rel = rel[rel.index("reymen/cereyan/") + 15:]

        norm = rel.replace("\\", "/")

        if norm not in existing:
            # Yeni dosya -> ekle
            content = fp.read_text("utf-8", errors="replace")[:5000]
            stem = fp.stem
            parts = rel.split("/")
            kat = "/".join(parts[:-1]) if len(parts) > 1 else "skills"
            # Mevcut formata uygun kaynak_url: file://skills/Skiller\\...
            prefix = parts[0]
            rest = "\\".join(parts[1:]) if len(parts) > 1 else ""
            kurl = f"file://{prefix}\\{rest}" if rest else f"file://{prefix}"

            con.execute(
                "INSERT INTO ogrenmeler "
                "(hedef, kategori, icerik, guven_skoru, basari_sayisi, hata_sayisi, "
                "son_kullanim, gecerlilik_tarihi, kaynak_url) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (stem, kat, content, 0.5, 1, 0, bugun, gec, kurl),
            )
            yeni += 1
            existing.add(norm)
            if yeni <= 5:
                print(f"  ✅ YENI: {norm}")
        # else: zaten var, guncelleme kontrolü yapılabilir (şimdilik atla)

    con.commit()
    con.close()

    print(f"\n=== SKILLS SYNC RAPORU ===")
    print(f"  Yeni eklenen:  {yeni}")
    print(f"  Guncellenen:   {guncel}")
    print(f"  Silinen:       {deleted}")
    print(f"  Toplam DB:     {sqlite3.connect(str(DB)).execute('SELECT COUNT(*) FROM ogrenmeler').fetchone()[0]}")

if __name__ == "__main__":
    main()
