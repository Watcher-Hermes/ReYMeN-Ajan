# DB Konsolidasyon Patterni — 10 DB → 1 memory.db

> **Tarih:** 2026-06-21  
> **Kaynak:** 10 SQLite DB → `reymen/cereyan/.ReYMeN/memory.db` (18.991 kayıt)

## Hedef Yapı

```
📁 reymen/cereyan/.ReYMeN/
├── 📊 memory.db          ← TEK hafıza DB'si
├── 📋 memory_taxonomy_5n1k.md
├── 📁 skills/            ← 1130 skill dosyası
└── 📁 ... (diğer eski DB'ler .bak olarak yedekte)
```

## Ne Zaman Kullanılır

- Çoklu SQLite DB'leri aynı veri yapısında birleştirilecekse
- Farklı kaynaklardan gelen hafıza/öğrenme verileri konsolide edilecekse
- Veri dağınıklığı tespit edildiğinde

## Adımlar

### 1. Tüm DB'leri Tara

```python
# Önce hangi DB'lerin gerçekten veri içerdiğini belirle
for root, dirs, files in os.walk(PROJE):
    for f in files:
        if f.endswith('.db'):
            conn = sqlite3.connect(path)
            c = conn.cursor()
            c.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = c.fetchall()
            # Boş/önemsiz tabloları filtrele
```

### 2. Unified Schema Oluştur

```sql
CREATE TABLE memory (
    id INTEGER PRIMARY KEY,
    kaynak TEXT,            -- hangi DB'den geldiği
    ne TEXT DEFAULT '',     -- 5N1K ana başlık
    alt_ne TEXT DEFAULT '', -- 5N1K alt başlık
    nerede TEXT DEFAULT '', -- 5N1K
    nasil TEXT DEFAULT '',  -- 5N1K
    neden TEXT DEFAULT '',  -- 5N1K
    kim TEXT DEFAULT '',    -- 5N1K
    baslik TEXT DEFAULT '', -- özet/başlık
    icerik TEXT DEFAULT '', -- içerik
    guven REAL DEFAULT 0.0, -- güven skoru
    tarih TEXT DEFAULT '',  -- zaman damgası
    etiket TEXT DEFAULT ''  -- etiketler
);
```

### 3. Veriyi Aktar

Her kaynak DB için:
1. Kaynağa bağlan
2. Her tabloyu oku (5N1K kolonları varsa al, yoksa boş geç)
3. `INSERT INTO memory (kaynak, ne, alt_ne, ...) VALUES (...)`

### 4. Temizlik

```python
# Case normalize
c.execute("UPDATE memory SET ne=LOWER(ne) WHERE ne != LOWER(ne)")

# Türkçe karakter düzelt
for tr, en in [('ü','u'),('ö','o'),('ı','i'),('ğ','g'),('ş','s'),('ç','c')]:
    c.execute(f"UPDATE memory SET ne=REPLACE(ne, '{tr}', '{en}')")

# FTS5 arama indeksi
c.execute("CREATE VIRTUAL TABLE memory_fts USING fts5(baslik, icerik)")
c.execute("INSERT INTO memory_fts SELECT id, baslik, icerik FROM memory")
```

## Pitfall'lar

| Sorun | Çözüm |
|:------|:------|
| **FTS5 tablosu ALTER edilemez** | Mapping tablosu (`_5n1k`) oluştur, asıl FTS tablosuna dokunma |
| **Bağlantı kapatılıp yeniden kullanılırsa** | `Cannot operate on a closed database` → Her sorgu için ayrı bağlantı aç veya bağlantıyı açık tut |
| **İki skills_index.db farklı veri** | Primary seç, secondary'yi primary ile merge et (ad bazlı dedup) |
| **NFKD normalize Türkçe harf düşürür** | Direkt char map kullan (`ü→u, ö→o, ı→i, ğ→g, ş→s, ç→c`), NFKD kullanma |
| **Case farkı ile duplicate başlıklar** | `LOWER(ne)` ile tüm başlıkları normalize et |
| **Yeni gelen veri hangi başlığa gidecek?** | mevcut `ne` listesinde varsa o başlığa, yoksa yeni başlık aç |

## Konsolidasyon Mapping'i (10 DB → 1)

| Kaynak DB | memory.kaynak | memory.ne kaynağı | Kayıt |
|:----------|:-------------|:------------------|:-----:|
| `ogrenmeler.db` | ogrenmeler | ne kolonu | 1.773 |
| `hafiza.db/kayitlar` | hafiza/kayit | ne kolonu | 2.462 |
| `hafiza.db/sessions` | hafiza/session | ne kolonu | 435 |
| `ogrenme.db` | ogrenme | ne kolonu | 228 |
| `state.db/messages` | state/mesaj | role→ne | 277 |
| `session.db/gunluk` | session/gunluk | ne kolonu | 83 |
| `skill_index.db/FTS5` | skill_index | skill_5n1k tablosu | 5.781 |
| `skills_index.db/FTS5` | skills_index | beceriler_5n1k tablosu | 7.983 |
| `hatalar.db` | hatalar | ne kolonu | 6 |
| `memory_fts.db` | memory_fts | hafiza_5n1k tablosu | 1 |
| **TOPLAM** | | | **18.991** |
