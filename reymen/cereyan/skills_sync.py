#!/usr/bin/env python3
"""
skills_sync.py — Skill .md dosyalarını OnceHafiza DB'sine senkronize eder.
Her 6 saatte bir cron ile çalışması için tasarlanmıştır.
Sadece _SKILL.md dosyalarını işler, reference/other dosyaları atlar.
"""

import os
import sys
import hashlib
from pathlib import Path

# Proje kökü
PROJE_KOK = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJE_KOK))

from reymen.cereyan.once_hafiza import kaydet, DB_YOLU
import sqlite3

# ── Yapılandırma ──────────────────────────────────────────────────────────

SKILLS_DIRS = [
    PROJE_KOK / "reymen" / "cereyan" / "skills" / "Skiller",
    PROJE_KOK / "reymen" / "cereyan" / "skills_yeni",
]

# Kategori eşleme: alt dizin adı → DB kategorisi
KATEGORI_MAP = {
    "AI_ML": "skill/ai-ml",
    "tor": "skill/tor",
    "voice": "skill/voice",
    "Windows": "skill/windows",
    "windows": "skill/windows",
    "DevOps": "skill/devops",
    "Github": "skill/github",
    "Gaming": "skill/gaming",
    "Guvenlik": "skill/security",
    "Kod": "skill/code",
    "Medya": "skill/media",
    "Research": "skill/research",
    "Test": "skill/test",
    "Verimlilik": "skill/productivity",
    "Egitim": "skill/education",
    "Yaratici": "skill/creative",
    "Ag": "skill/router",
    "Kullanici": "skill/user-preferences",
    "apple": "skill/apple",
    "android": "skill/android",
    "cross-platform": "skill/cross-platform",
    "smart-home": "skill/smart-home",
}

def _kategori_bul(dizin_adi: str) -> str:
    """Alt dizin adından kategori belirle."""
    return KATEGORI_MAP.get(dizin_adi, f"skill/{dizin_adi.lower()}")

def _hedef_bul(fname: str) -> str:
    """Dosya adından hedef (benzersiz anahtar) belirle."""
    name = fname
    if name.endswith("_SKILL.md"):
        name = name[:-len("_SKILL.md")]
    elif name.endswith(".md"):
        name = name[:-len(".md")]
    return name.strip()

def _icerik_hash(icerik: str) -> str:
    """İçerik için MD5 hash (değişiklik tespiti için)."""
    return hashlib.md5(icerik.encode("utf-8"), usedforsecurity=False).hexdigest()

def _db_icerik_hash(hedef: str, kategori: str) -> str | None:
    """DB'deki mevcut kaydın içerik hash'ini al."""
    try:
        con = sqlite3.connect(str(DB_YOLU), timeout=5)
        cur = con.execute(
            "SELECT icerik FROM ogrenmeler WHERE hedef = ? AND kategori = ?",
            (hedef, kategori)
        )
        row = cur.fetchone()
        con.close()
        if row:
            return _icerik_hash(row[0])
        return None
    except Exception:
        return None

def _tarama_yap() -> list:
    """Tüm skill dizinlerini tara, _SKILL.md dosyalarını bul."""
    sonuclar = []
    for skills_dir in SKILLS_DIRS:
        if not skills_dir.exists():
            print(f"  [UYARI] Dizin mevcut değil: {skills_dir}")
            continue
        
        for dirpath, dirnames, filenames in os.walk(skills_dir):
            for fname in filenames:
                if not fname.endswith("_SKILL.md"):
                    continue
                
                full_path = Path(dirpath) / fname
                rel_path = full_path.relative_to(skills_dir)
                
                # Alt dizin adını al (ilk seviye)
                parts = rel_path.parts
                alt_dizin = parts[0] if len(parts) > 0 else ""
                
                kategori = _kategori_bul(alt_dizin)
                hedef = _hedef_bul(fname)
                
                # Dosya içeriğini oku
                try:
                    icerik = full_path.read_text(encoding="utf-8", errors="replace")
                except Exception as e:
                    print(f"  [HATA] Okunamadı: {full_path} — {e}")
                    icerik = ""
                
                sonuclar.append((str(rel_path), hedef, kategori, str(full_path), fname, icerik))
    
    return sonuclar

def _senkronize(sonuclar: list) -> dict:
    """Bulunan skill dosyalarını DB'ye senkronize et."""
    sayac = {"eklenen": 0, "guncellenen": 0, "atlanan": 0, "hata": 0}
    
    for rel_path, hedef, kategori, full_path, fname, icerik in sonuclar:
        try:
            # İçeriği kısalt (ilk 5000 karakter)
            icerik_kisa = icerik[:5000]
            
            # Önce DB'de var mı kontrol et
            mevcut_hash = _db_icerik_hash(hedef, kategori)
            
            if mevcut_hash is None:
                # Yeni kayıt
                kaydet(
                    hedef=hedef,
                    kategori=kategori,
                    icerik=icerik_kisa,
                    basari=True,
                    kaynak_url=f"file://skills/Skiller/{rel_path.replace(os.sep, '/')}"
                )
                sayac["eklenen"] += 1
                print(f"  + {kategori}/{hedef}")
            else:
                # Var, içerik değişmiş mi kontrol et
                yeni_hash = _icerik_hash(icerik_kisa)
                if yeni_hash != mevcut_hash:
                    kaydet(
                        hedef=hedef,
                        kategori=kategori,
                        icerik=icerik_kisa,
                        basari=True,
                        kaynak_url=f"file://skills/Skiller/{rel_path.replace(os.sep, '/')}"
                    )
                    sayac["guncellenen"] += 1
                    print(f"  ~ {kategori}/{hedef}")
                else:
                    sayac["atlanan"] += 1
        except Exception as e:
            print(f"  ! HATA: {kategori}/{hedef} — {e}")
            sayac["hata"] += 1
    
    return sayac


def calistir() -> dict:
    """Ana çalıştırma fonksiyonu - cron tarafından çağrılır."""
    print("=" * 60)
    print("  SKILL → HAFIZA SENKRONİZASYONU")
    print("=" * 60)
    print(f"  DB: {DB_YOLU}")
    print(f"  Zaman: {__import__('datetime').datetime.now().isoformat()}")
    print()
    
    # 1. Tara
    print("[1/2] Skill dosyaları taranıyor...")
    sonuclar = _tarama_yap()
    print(f"  Bulunan _SKILL.md dosyası: {len(sonuclar)}")
    print()
    
    # 2. Senkronize et
    print("[2/2] DB senkronize ediliyor...")
    sonuc = _senkronize(sonuclar)
    print()
    
    # 3. Rapor
    print("-" * 60)
    print("  ÖZET")
    print("-" * 60)
    print(f"  Toplam skill dosyası: {len(sonuclar)}")
    print(f"  Yeni eklenen:         {sonuc['eklenen']}")
    print(f"  Güncellenen:          {sonuc['guncellenen']}")
    print(f"  Atlanan (değişmeyen): {sonuc['atlanan']}")
    print(f"  Hata:                 {sonuc['hata']}")
    print("=" * 60)
    
    return sonuc


if __name__ == "__main__":
    calistir()
