# Hafıza Sistemi Pitfall'ları: JSON Index & FTS5 Stale Cache

## Pitfall 1: SQL Result Index Kayması

**Tarih:** 2026-06-25
**Dosya:** `reymen/sistem/once_hafiza.py` satır 245

### Sorun
`hafizada_ara()` içinde SQL sonucu yanlış index ile okunuyordu:

```python
# SQL: SELECT hedef, cozum, kaynak, basari_sayisi, hata_sayisi, ...
# Index:    0      1      2        3              4

# YANLIŞ (row[4] = hata_sayisi, integer):
sonuc = {"hedef": row[0], "cozum": row[1], "kaynak": row[4] or "ogrenme"}

# DOĞRU (row[2] = kaynak, string):
sonuc = {"hedef": row[0], "cozum": row[1], "kaynak": row[2] or "ogrenme"}
```

### Belirti
- `kaynak` field'ı integer (0, 1, 5...) olarak dönüyor
- JSON serialization hata veriyor veya bozuk JSON üretiyor
- Log'da `Referanslar: {"anahtar": "dri...` şeklinde kesik JSON görünüyor

### Kök Neden
SQL SELECT sırası ile Python dict index sırası uyuşmuyordu. `row[4]` = `hata_sayisi` (integer), ama `kaynak` = `row[2]` olmalıydı.

### Düzeltme
```python
# row[4] → row[2]
sonuc = {"hedef": row[0], "cozum": row[1], "kaynak": row[2] or "ogrenme", "guven": guven_skor}
```

### Önleme
SQL result mapping yaparken:
1. SELECT sütunlarını numaralandır
2. Her index'in hangi field'a karşılık geldiğini comment olarak yaz
3. Named tuple veya dict factory kullan (`con.row_factory = sqlite3.Row`)

---

## Pitfall 2: FTS5 Stale Cache Hit (Bozuk Skill Dosyası)

**Tarih:** 2026-06-25

### Sorun
Daha önceki bir başarısız denemeden otomatik oluşturulan bozuk skill dosyası FTS5 index'te kaldı. Aynı sorgu tekrar geldiğinde FTS5 bu bozuk dosyayı buldu, `hafizada_ara()` onu "bulundu" saydı ve bozuk içeriği döndürdü.

### Belirti
- `[OnceHafiza] 🔍 Skills FTS5'te bulundu: skills/altının_ons_değeri_nedirreferanslar`
- Dosya içeriği kesik/truncated (yarım cümleler)
- Model bu bozuk veriyi kullanarak "Bilmiyorum" veya anlamsız cevap üretiyor

### Kök Neden
`beceri_kristallestir()` veya `yetenek_olustur()` tarafından oluşturulan skill dosyası:
1. Dosya adı bozuk (`altının_ons_değeri_nedirreferanslar` — "referanslar" ad'a yapışmış)
2. İçerik truncated (yarım JSON, kesik cümleler)
3. FTS5 index'ten silinmemiş

### Düzeltme
1. Bozuk dosyayı sil: `rm skills/altının_ons_değeri_nedirreferanslar.md`
2. FTS5 index'ten sil: `DELETE FROM beceriler WHERE ad = '...'`
3. Index'i yenile: `skill_index_yenile(zorla=True)`

### Önleme
`hafizada_ara()` döndürdükten sonra içerik doğrulama yap:

```python
sonuc = oh.hafizada_ara(hedef)
if sonuc:
    # İçerik doğrulama
    icerik = sonuc.get("cozum", "")
    if len(icerik) < 20 or icerik.endswith("...") or "truncated" in icerik.lower():
        logger.warning("[OnceHafiza] Bozuk cache hit — ignore: %s", sonuc.get("hedef"))
        sonuc = None  # Cache miss gibi davran
```

### Düzenli Bakım
```python
# FTS5 index'te dosyası olmayan kayıtları temizle
import sqlite3, os
con = sqlite3.connect("skills_index.db")
rows = con.execute("SELECT rowid, kaynak FROM beceriler").fetchall()
for rowid, kaynak in rows:
    if kaynak and not os.path.exists(kaynak):
        con.execute("DELETE FROM beceriler WHERE rowid = ?", (rowid,))
con.commit()
```

---

## Pitfall 3: Hızlı Yol Web Aramasını Atlıyor

**Tarih:** 2026-06-25
**Dosya:** `reymen/sistem/main.py` satır 676-700

### Sorun
`run_conversation()` içinde "hızlı yol" (`?` içerdiği için `_tip_hizli = "bilgi"`) fiyat/güncel veri sorgularını doğrudan LLM'e gönderiyor, web aramasını tamamen atlıyordu.

### Belirti
- "Altın ons fiyatı nedir?" → LLM "Bilmiyorum" diyor veya CJK spam üretiyor
- Log'da web arama tetikleyicisi görünmüyor
- `auto_web_search.py` hiç çağrılmıyor

### Düzeltme
Güncel kelime tespiti ile hızlı yolu bypass et:

```python
_GUNCEL_KELIMELER = [
    "fiyat", "fiyatı", "fiyati", "kur", "dolar", "euro", "altın", "altin",
    "bitcoin", "borsa", "hava", "haber", "deprem", "maç", "skor",
    "kaç tl", "kac tl", "ne kadar", "güncel", "bugün", "şimdi",
]
_guncel_sorgu = any(k in _h for k in _GUNCEL_KELIMELER)

if _guncel_sorgu:
    _tip_hizli = "karmasik"  # ReAct'e düş → web araması tetiklenir
```

### Kural
Hızlı yol SADECE selam/sohbet için. Güncel veri gerektiren sorgular HER ZAMAN ReAct döngüsüne gitmeli.
