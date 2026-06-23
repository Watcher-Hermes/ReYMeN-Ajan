#!/usr/bin/env python3
"""
duplicate_module_detector.py — ReYMeN drift/duplicate modül tespit aracı.
Her cycle başında çalıştırılır, mimari sapmaları raporlar.

Tespit Eder:
1. Aynı/similar işlevli birden çok dosya (önbellek mekanizmasız)
2. "Yazıldı ama çağrılmıyor" modüller (tanımlı ama import edilmemiş)
3. Farklı DB yollarına yazan benzer modüller
4. Eski alias isimleri kullanan referanslar
"""

import ast
import os
import sys
from collections import defaultdict
from pathlib import Path

# ── Yapılandırma ──────────────────────────────────────────────────────
PROJE_DIZINI = Path(__file__).resolve().parent.parent  # hermes_projesi/
HASSAS_KONUMLAR = [
    "reymen/cereyan",
    "reymen/sistem",
    "reymen/hafiza",
    "tools/memory_providers",
    "gateway/platforms",
]
BENZERLIK_ESIK = 0.65  # Jaccard benzerlik eşiği
YOK_SAYILAN_MODUL_KALIBI = [
    "bir", "ornek", "test", "__pycache__", ".pyc", ".md",
]
ASLA_TARA = {"__pycache__", "venv", ".git", "node_modules", "__init__.py"}


def _jaccard(a: set, b: set) -> float:
    """İki küme arasındaki Jaccard benzerliği."""
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def _dosya_adi_kumeleri(dosya: Path) -> set[str]:
    """Dosya adından anlamlı token seti çıkar."""
    ad = dosya.stem.lower()
    for ch in "_-.":
        ad = ad.replace(ch, " ")
    return set(filter(None, ad.split()))


def _hesap_kontrol(path: Path) -> list[str]:
    """Bir Python dosyasının fonksiyon/sınıf isimlerini çıkar."""
    isimler = []
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            tree = ast.parse(f.read(), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                isimler.append(f"def:{node.name}")
            elif isinstance(node, ast.ClassDef):
                isimler.append(f"class:{node.name}")
    except (SyntaxError, Exception):
        pass
    return isimler


# ── Ana Tarama ────────────────────────────────────────────────────────

def tara_benzer(proje: Path) -> list[dict]:
    """Benzer dosya adlarına sahip modülleri bul."""
    tum_dosyalar = []
    for hassas in HASSAS_KONUMLAR:
        dizin = proje / hassas
        if not dizin.exists():
            continue
        for f in dizin.rglob("*.py"):
            if f.name in ASLA_TARA:
                continue
            if f.stem in YOK_SAYILAN_MODUL_KALIBI:
                continue
            tum_dosyalar.append(f)

    kumeler = {f: _dosya_adi_kumeleri(f) for f in tum_dosyalar}
    eslesen = []
    gorulen = set()

    for i, (f1, k1) in enumerate(kumeler.items()):
        if f1 in gorulen:
            continue
        for j, (f2, k2) in enumerate(kumeler.items()):
            if j <= i or f2 in gorulen:
                continue
            skor = _jaccard(k1, k2)
            if skor >= BENZERLIK_ESIK:
                # Aynı dosya değil mi kontrol et
                if f1.resolve() != f2.resolve():
                    eslesen.append({
                        "dosya1": str(f1.relative_to(proje)),
                        "dosya2": str(f2.relative_to(proje)),
                        "benzerlik": round(skor, 2),
                    })
                    gorulen.add(f1)
                    gorulen.add(f2)

    return eslesen


def tara_kullanilmayan(proje: Path) -> list[str]:
    """Import edilmemiş .py dosyalarını bul."""
    tum_py = set()
    for hassas in HASSAS_KONUMLAR:
        dizin = proje / hassas
        if not dizin.exists():
            continue
        for f in dizin.rglob("*.py"):
            if f.name not in ASLA_TARA and f.stem not in YOK_SAYILAN_MODUL_KALIBI:
                tum_py.add(f)

    # Tüm import'ları tara
    tum_importlar = set()
    for f in tum_py:
        try:
            metin = f.read_text(encoding="utf-8", errors="replace")
            for satir in metin.split("\n"):
                s = satir.strip()
                if s.startswith("import ") or s.startswith("from "):
                    # import x.y.z → x
                    mod = s.split()[1].split(".")[0]
                    tum_importlar.add(mod)
        except Exception:
            pass

    # Proje dışı import'ları ele
    proje_moduller = {f.stem for f in tum_py}
    kullanilmayan = []
    for f in tum_py:
        if f.stem not in tum_importlar and f.stem in proje_moduller:
            # __init__ kontrolü: __init__ olabilir
            if f.name == "__init__.py":
                continue
            kullanilmayan.append(str(f.relative_to(proje)))

    return kullanilmayan


def tara_farkli_db_yazan(proje: Path) -> list[dict]:
    """Farkl√Ω DB yollarına yazan benzer modülleri bul."""
    db_referanslari = defaultdict(list)

    for f in proje.rglob("*.py"):
        if any(p in str(f) for p in [".git", "__pycache__", "venv"]):
            continue
        try:
            metin = f.read_text(encoding="utf-8", errors="replace")
            for satir in metin.split("\n"):
                s = satir.strip().lower()
                if ".db" in s and ("connect(" in s or "path/" in s):
                    db_adi = s.split(".db")[0].split()[-1].strip("'\"")
                    db_referanslari[db_adi].append(
                        str(f.relative_to(proje))
                    )
        except Exception:
            pass

    # Aynı DB'ye yazan birden çok dosya var mı?
    sorunlu = []
    for db_adi, dosyalar in db_referanslari.items():
        if len(dosyalar) > 1:
            sorunlu.append({
                "db": db_adi,
                "dosyalar": dosyalar,
            })
    return sorunlu


def tara_eski_alias(proje: Path) -> list[str]:
    """Eski alias isimleri kullanan referansları bul."""
    eski_isimler = [
        "_cereyan_benzerlik_skoru",  # _cereyan_benzerlik oldu
        "_cereyan_eski_temizle",     # _cereyan_temizle oldu
        "_cereyan_belirsiz_cozumle", # _cereyan_belirsiz_cozum oldu
        "cereyan_once_hafiza",       # eski import
        "system_once_hafiza",        # yanlış yazım
    ]
    bulunan = []
    for f in proje.rglob("*.py"):
        if any(p in str(f) for p in [".git", "__pycache__", "venv"]):
            continue
        try:
            metin = f.read_text(encoding="utf-8", errors="replace")
            for eski in eski_isimler:
                if eski in metin:
                    bulunan.append(
                        f"{str(f.relative_to(proje))}: `{eski}`"
                    )
        except Exception:
            pass
    return bulunan


def raporla(proje: Path = PROJE_DIZINI) -> dict:
    """Tüm taramaları çalıştır, rapor döndür."""
    return {
        "benzer_moduller": tara_benzer(proje),
        "kullanilmayan_moduller": tara_kullanilmayan(proje),
        "farkli_db_yazanlar": tara_farkli_db_yazan(proje),
        "eski_alias_referanslari": tara_eski_alias(proje),
    }


def raporu_yazdir(sonuc: dict) -> str:
    """Raporu insan okunabilir formatta yazdır."""
    satirlar = ["📋 DUPLICATE MODULE DETECTOR — RAPOR"]
    satirlar.append("=" * 50)

    # 1) Benzer modüller
    satirlar.append(f"\n🔁 Benzer modüller ({len(sonuc['benzer_moduller'])}):")
    if sonuc['benzer_moduller']:
        for b in sonuc['benzer_moduller']:
            satirlar.append(f"  • {b['dosya1']} ↔ {b['dosya2']} ({b['benzerlik']})")
    else:
        satirlar.append("  ✅ Temiz — benzer modül yok")

    # 2) Kullanılmayan modüller
    satirlar.append(f"\n📭 Kullanılmayan modüller ({len(sonuc['kullanilmayan_moduller'])}):")
    if sonuc['kullanilmayan_moduller']:
        for k in sonuc['kullanilmayan_moduller']:
            satirlar.append(f"  • {k}")
    else:
        satirlar.append("  ✅ Temiz — kullanılmayan yok")

    # 3) Farklı DB yazanlar
    satirlar.append(f"\n🗄️  Farklı DB yazan benzer modüller ({len(sonuc['farkli_db_yazanlar'])}):")
    if sonuc['farkli_db_yazanlar']:
        for d in sonuc['farkli_db_yazanlar']:
            satirlar.append(f"  • {d['db']}.db → {len(d['dosyalar'])} dosya:")
            for dos in d['dosyalar']:
                satirlar.append(f"    - {dos}")
    else:
        satirlar.append("  ✅ Temiz — aynı DB'ye tek kaynak")

    # 4) Eski alias referansları
    satirlar.append(f"\n🔄 Eski alias referansları ({len(sonuc['eski_alias_referanslari'])}):")
    if sonuc['eski_alias_referanslari']:
        for e in sonuc['eski_alias_referanslari']:
            satirlar.append(f"  • {e}")
    else:
        satirlar.append("  ✅ Temiz — eski alias yok")

    # 5) Özet
    toplam = (
        len(sonuc['benzer_moduller'])
        + len(sonuc['kullanilmayan_moduller'])
        + len(sonuc['farkli_db_yazanlar'])
        + len(sonuc['eski_alias_referanslari'])
    )
    satirlar.append(f"\n{'=' * 50}")
    satirlar.append(f"📊 Özet: {toplam} sorun {'bulundu' if toplam else 'yok, temiz'}")

    return "\n".join(satirlar)


if __name__ == "__main__":
    sonuc = raporla()
    print(raporu_yazdir(sonuc))
