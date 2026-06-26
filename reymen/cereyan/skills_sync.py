#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
skills_sync.py — reymen/cereyan/skills/ altindaki .md dosyalarini
OnceHafiza DB'sine kaydeder/gunceller.

Kullanim: 
  python3 reymen/cereyan/skills_sync.py

Cron: Her 6 saatte bir calisir.
    0 */6 * * * cd /proje && python3 reymen/cereyan/skills_sync.py

Versiyon: 3 (final)
"""
import sqlite3, hashlib
from datetime import date, timedelta
from pathlib import Path

# ── Yollar ────────────────────────────────────────────────────────────────
DB = Path("reymen/cereyan/.ReYMeN/ogrenmeler.db")
SKILLS_DIR = Path("reymen/cereyan/skills")
ROOT = Path("reymen/cereyan")

def log(msg: str):
    from datetime import datetime
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")

def baglan():
    con = sqlite3.connect(str(DB), timeout=30)
    con.execute("PRAGMA busy_timeout=30000")
    return con

def normalize_kaynak_url(kurl: str) -> str | None:
    """DB'deki kaynak_url'yi normalize edilmis relpath'e cevir."""
    if kurl.startswith("file://"):
        kurl = kurl[7:]
    kurl = kurl.replace("\\", "/")
    idx = kurl.lower().find("skills/")
    if idx >= 0:
        return kurl[idx:]
    return None

def build_db_index(con) -> dict[str, tuple[int, str]]:
    """
    DB'deki skills kayitlarini normalize_path -> (id, icerik) seklinde indexle.
    Her dosya icin sadece ILK kaydi al (chunk'larin ilki).
    """
    cur = con.execute(
        "SELECT id, kaynak_url, icerik FROM ogrenmeler "
        "WHERE kategori LIKE 'skills%' AND kaynak_url IS NOT NULL "
        "ORDER BY id"
    )
    index = {}
    for rid, kurl, icerik in cur.fetchall():
        norm = normalize_kaynak_url(str(kurl))
        if norm and norm not in index:
            index[norm] = (rid, str(icerik or ""))
    return index

def sync():
    log("=== SKILLS SYNC BASLADI ===")
    con = baglan()
    
    # DB index'ini olustur
    db_index = build_db_index(con)
    log(f"DB'de essiz skills kaydi: {len(db_index)}")
    
    # Dizindeki tum .md dosyalarini tara
    md_files = sorted(SKILLS_DIR.rglob("*.md"))
    log(f"Dizinde .md dosyasi: {len(md_files)}")
    
    yeni = 0
    guncellenen = 0
    ayni = 0
    bugun = date.today().isoformat()
    gec = (date.today() + timedelta(days=180)).isoformat()
    
    for fp in md_files:
        try:
            rel = fp.relative_to(ROOT).as_posix()
        except ValueError:
            continue
        
        norm = rel.replace("\\", "/")
        file_content = fp.read_text("utf-8", errors="replace")[:5000]
        file_hash = hashlib.sha256(file_content.encode()).hexdigest()
        
        if norm in db_index:
            # Varolan kayit -> hash karsilastir
            rid, db_icerik = db_index[norm]
            db_hash = hashlib.sha256(db_icerik.encode()).hexdigest()
            
            if db_hash != file_hash:
                con.execute(
                    "UPDATE ogrenmeler SET icerik = ?, guncelleme = datetime('now') WHERE id = ?",
                    (file_content, rid)
                )
                guncellenen += 1
            else:
                ayni += 1
        else:
            # Yeni dosya -> ekle
            parts = rel.split("/")
            stem = fp.stem
            kat = "/".join(parts[:-1]) if len(parts) > 1 else "skills"
            # Legacy format: file://skills/Klasor\AltKlasor\dosya.md
            prefix = parts[0]
            rest = "\\".join(parts[1:]) if len(parts) > 1 else ""
            kurl = f"file://{prefix}\\{rest}" if rest else f"file://{prefix}"
            
            con.execute(
                "INSERT INTO ogrenmeler "
                "(hedef, kategori, icerik, guven_skoru, basari_sayisi, hata_sayisi, "
                "son_kullanim, gecerlilik_tarihi, kaynak_url) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (stem, kat, file_content, 0.5, 1, 0, bugun, gec, kurl),
            )
            yeni += 1
            db_index[norm] = (con.execute("SELECT last_insert_rowid()").fetchone()[0], file_content)
    
    con.commit()
    con.close()
    
    # Rapor
    log(f"--- RAPOR ---")
    log(f"  Yeni eklenen:  {yeni}")
    log(f"  Guncellenen:   {guncellenen}")
    log(f"  Degismeyen:    {ayni}")
    log(f"  Toplam DB:     {sqlite3.connect(str(DB)).execute('SELECT COUNT(*) FROM ogrenmeler').fetchone()[0]}")
    log("=== SKILLS SYNC TAMAM ===")

if __name__ == "__main__":
    sync()
