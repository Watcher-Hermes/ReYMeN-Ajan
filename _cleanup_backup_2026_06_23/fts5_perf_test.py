# -*- coding: utf-8 -*-
"""FTS5 memory.db performans testi"""
import sqlite3, time, statistics, os, sys

DB = r"C:\Users\marko\Desktop\Reymen Proje\hermes_projesi\reymen\cereyan\.ReYMeN\memory.db"

def bolum(baslik):
    print(f"\n{'='*60}")
    print(f"  {baslik}")
    print('='*60)

con = sqlite3.connect(DB, check_same_thread=False)
cur = con.cursor()

# ── 1. Şema keşfi ────────────────────────────────────────────
bolum("1. ŞEMA & TABLO YAPISI")
cur.execute("SELECT name, type FROM sqlite_master ORDER BY type, name")
rows = cur.fetchall()
for r in rows:
    print(f"  [{r[1]:6s}]  {r[0]}")

# ── 2. Kayıt sayıları ────────────────────────────────────────
bolum("2. KAYIT SAYILARI")
cur.execute("""
    SELECT name FROM sqlite_master
    WHERE type='table'
      AND name NOT LIKE '%_content'
      AND name NOT LIKE '%_segdir'
      AND name NOT LIKE '%_segments'
      AND name NOT LIKE '%_stat'
      AND name NOT LIKE '%_docsize'
      AND name NOT LIKE '%_data'
      AND name NOT LIKE '%_idx'
      AND name NOT LIKE '%_config'
""")
tablolar = [r[0] for r in cur.fetchall()]
for t in tablolar:
    try:
        cur.execute(f"SELECT COUNT(*) FROM [{t}]")
        n = cur.fetchone()[0]
        print(f"  {t:<30s}: {n:>8,} kayıt")
    except Exception as e:
        print(f"  {t}: HATA - {e}")

# ── 3. FTS5 tablosu sütunları ────────────────────────────────
bolum("3. FTS5 TABLO SÜTUNLARI")
fts_tablolar = [t for t in tablolar if "fts" in t.lower() or "memory" in t.lower() or "memories" in t.lower()]
if not fts_tablolar:
    # Hepsini dene
    fts_tablolar = tablolar
print(f"  Test edilecek tablolar: {fts_tablolar}")
for t in fts_tablolar[:3]:
    try:
        cur.execute(f"SELECT * FROM [{t}] LIMIT 1")
        cols = [d[0] for d in cur.description]
        print(f"\n  [{t}] sütunlar: {cols}")
        cur.execute(f"SELECT * FROM [{t}] LIMIT 2")
        for row in cur.fetchall():
            for col, val in zip(cols, row):
                v = str(val)[:80] if val else "NULL"
                print(f"    {col}: {v}")
            print()
    except Exception as e:
        print(f"  {t}: {e}")

# ── 4. FTS5 performans testleri ──────────────────────────────
bolum("4. FTS5 ARAMA PERFORMANSI")

ARAMA_SORGULARI = [
    ("Tek kelime", "python"),
    ("Tek kelime", "telegram"),
    ("Tek kelime", "skill"),
    ("Türkçe kelime", "hafıza"),
    ("Türkçe kelime", "güven"),
    ("Çok kelime (OR)", "python OR nmap"),
    ("Önek (prefix)", "deep*"),
    ("Cümle", "deepseek api"),
    ("Uzun sorgu", "windows automation skill hermes"),
    ("Nadir terim", "cereyan"),
]

TEKRAR = 10

# FTS5 tablosunu bul
fts_tablo = None
for t in tablolar:
    try:
        # FTS5 MATCH testi
        cur.execute(f"SELECT COUNT(*) FROM [{t}] WHERE [{t}] MATCH 'python'")
        fts_tablo = t
        print(f"  FTS5 tablosu: {t}")
        break
    except:
        continue

if not fts_tablo:
    print("  UYARI: FTS5 MATCH destekli tablo bulunamadı!")
    print("  LIKE ile test yapılacak...")
    # LIKE fallback
    for t in tablolar[:3]:
        try:
            cur.execute(f"SELECT COUNT(*) FROM [{t}] WHERE CAST(content AS TEXT) LIKE '%python%'")
            print(f"  LIKE test tablosu: {t}")
            fts_tablo = t
            break
        except:
            continue

print(f"\n  {'Sorgu Tipi':<20} {'Sorgu':<30} {'Sonuç':>7} {'Ort ms':>8} {'Min ms':>8} {'Max ms':>8} {'p95 ms':>8}")
print(f"  {'-'*88}")

for tip, sorgu in ARAMA_SORGULARI:
    sureler = []
    sonuc_n = 0
    for _ in range(TEKRAR):
        t0 = time.perf_counter()
        try:
            if fts_tablo:
                try:
                    cur.execute(f"SELECT COUNT(*) FROM [{fts_tablo}] WHERE [{fts_tablo}] MATCH ?", (sorgu,))
                except:
                    # Sütun adıyla dene
                    cols = [d[0] for d in cur.description] if cur.description else []
                    if cols:
                        cur.execute(f"SELECT COUNT(*) FROM [{fts_tablo}] WHERE {cols[0]} MATCH ?", (sorgu,))
            sonuc_n = cur.fetchone()[0]
        except Exception as e:
            sonuc_n = -1
        t1 = time.perf_counter()
        sureler.append((t1 - t0) * 1000)

    ort = statistics.mean(sureler)
    mn  = min(sureler)
    mx  = max(sureler)
    p95 = sorted(sureler)[int(TEKRAR * 0.95)]
    print(f"  {tip:<20} {sorgu:<30} {sonuc_n:>7} {ort:>8.2f} {mn:>8.2f} {mx:>8.2f} {p95:>8.2f}")

# ── 5. Full scan karşılaştırması ─────────────────────────────
bolum("5. FTS5 vs FULL SCAN KARŞILAŞTIRMASI")

# Full scan (LIKE)
sureler_like = []
for _ in range(TEKRAR):
    t0 = time.perf_counter()
    try:
        cur.execute(f"SELECT COUNT(*) FROM [{tablolar[0]}] WHERE CAST(rowid AS TEXT) LIKE '%1%'")
        cur.fetchone()
    except:
        pass
    sureler_like.append((time.perf_counter() - t0) * 1000)

# FTS5 arama
sureler_fts = []
for _ in range(TEKRAR):
    t0 = time.perf_counter()
    try:
        if fts_tablo:
            cur.execute(f"SELECT COUNT(*) FROM [{fts_tablo}] WHERE [{fts_tablo}] MATCH 'python'")
            cur.fetchone()
    except:
        pass
    sureler_fts.append((time.perf_counter() - t0) * 1000)

print(f"  Full scan (rowid LIKE)  : ort {statistics.mean(sureler_like):.2f} ms")
print(f"  FTS5 MATCH (python)     : ort {statistics.mean(sureler_fts):.2f} ms")
if statistics.mean(sureler_like) > 0 and statistics.mean(sureler_fts) > 0:
    oran = statistics.mean(sureler_like) / statistics.mean(sureler_fts)
    print(f"  FTS5 hız avantajı       : {oran:.1f}x")

# ── 6. DB sağlık durumu ──────────────────────────────────────
bolum("6. DB SAĞLIK & İSTATİSTİK")

db_boyut = os.path.getsize(DB) / (1024*1024)
print(f"  Dosya boyutu     : {db_boyut:.2f} MB")

try:
    cur.execute("PRAGMA integrity_check")
    ic = cur.fetchone()[0]
    print(f"  Integrity check  : {ic}")
except Exception as e:
    print(f"  Integrity check  : HATA - {e}")

try:
    cur.execute("PRAGMA page_count")
    pc = cur.fetchone()[0]
    cur.execute("PRAGMA page_size")
    ps = cur.fetchone()[0]
    print(f"  Page count       : {pc:,}")
    print(f"  Page size        : {ps} bytes")
    print(f"  Kullanılan alan  : {pc*ps/1024/1024:.2f} MB")
except Exception as e:
    print(f"  Sayfa bilgisi    : HATA - {e}")

try:
    cur.execute("PRAGMA freelist_count")
    fl = cur.fetchone()[0]
    print(f"  Boş sayfa sayısı : {fl:,}  {'(VACUUM önerilir)' if fl > 100 else '(temiz)'}")
except:
    pass

try:
    cur.execute("PRAGMA wal_checkpoint")
    print(f"  WAL checkpoint   : {cur.fetchone()}")
except:
    pass

# ── 7. Kapasite & büyüme tahmini ────────────────────────────
bolum("7. KAPASİTE & BÜYÜME TAHMİNİ")
try:
    cur.execute(f"SELECT COUNT(*) FROM [{tablolar[0]}]")
    toplam = cur.fetchone()[0]
    mb_per_kayit = db_boyut / max(toplam, 1)
    print(f"  Mevcut kayıt sayısı  : {toplam:,}")
    print(f"  Kayıt başına alan    : {mb_per_kayit*1024:.1f} KB")
    for hedef in [50000, 100000, 500000]:
        tahmini_mb = hedef * mb_per_kayit
        print(f"  {hedef:>7,} kayıtta tahmini boyut: {tahmini_mb:.1f} MB")
    print(f"\n  FTS5 önerilen limit  : ~1-5 milyon kayıt (sqlite FTS5 için)")
    print(f"  Mevcut doluluk oranı : %{toplam/1000000*100:.2f} (1M hedef baz alınırsa)")
except Exception as e:
    print(f"  Kapasite tahmini: HATA - {e}")

# ── 8. Sonuç değerlendirmesi ────────────────────────────────
bolum("8. SONUÇ DEĞERLENDİRMESİ")
try:
    ort_fts = statistics.mean(sureler_fts)
    if ort_fts < 1:
        durum = "MUKEMMEL (< 1ms)"
    elif ort_fts < 5:
        durum = "IYI (1-5ms)"
    elif ort_fts < 20:
        durum = "KABUL EDILEBILIR (5-20ms)"
    elif ort_fts < 100:
        durum = "YAVASH (20-100ms)"
    else:
        durum = "KRITIK (> 100ms) — VACUUM veya yeniden indeks gerekli"
    print(f"  Performans durumu : {durum}")
    print(f"  Ortalama FTS5 arama süresi: {ort_fts:.2f} ms")
    print(f"  Kapasite durumu   : {'NORMAL' if toplam < 100000 else 'İZLEME GEREKLİ'}")
except:
    pass

con.close()
print("\n[TEST TAMAMLANDI]")
