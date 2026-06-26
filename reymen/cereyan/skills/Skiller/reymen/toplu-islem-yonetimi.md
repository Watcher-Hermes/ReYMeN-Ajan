---
name: toplu-islem-yonetimi
title: "Toplu İşlem Yönetimi (Batch Task Management)"
tags: [reymen, batch, automation, workflow, categorization]
description: "Use when the user says 'hepsini onaysız yap', 'batch olarak devam et', '2 dakika sessiz = onay', or any mass/batch operation. Governs silent-approval workflow, file categorization at scale, deduplication, and 5N1K taxonomy application."
version: 1.2.0
audience: user
triggers:
  - sessiz onay
  - onaysız
  - 2 dakika
  - batch
  - toplu
  - kategori
  - 5n1k
  - dedup
  - uncategorized
---

# Toplu İşlem Yönetimi

## Sessiz Onay Protokolü

Kullanıcı "hepsini onaysız yap" veya "sessiz onaysız geçerli" dediğinde:

1. **2 dakika sessiz = otomatik onay** — Kullanıcı yanıt vermezse en mantıklı seçenekle devam et
2. **Batch modu** — Her adım için onay bekleme, sırayla işle
3. **Hata durumu** — Hata alırsan alternatif dene, başarısız olanı not et, kalanla devam et
4. **Sonuç raporu** — Batch bitince özet ver: kaç başarılı, kaç hata, ne kadar sürdü

```
Kullanıcı: "Skiller tamami onaysız bitene kadar devam et"
→ Batch mod aktif
→ Her işlem sonrası 2dk bekle
→ Cevap yoksa en mantıklı seçenekle devam
→ Hataları logla, batch'i durdurma
→ Sonunda özet raporu ver
```

## Toplu Kategorilendirme (Bulk File Organization)

Büyük dosya gruplarını (.md, .py, .json) kategorilere ayırırken:

### 1. Analiz Aşaması
```python
# Önce yapıyı anla
dosyalar = os.listdir(hedef_dizin)
prefix_counts = Counter(d.split('_')[0] for d in dosyalar)
# full_X + X çiftlerini tespit et
```

### 2. Kategorilendirme Stratejisi
- Dosya adı prefix'lerine göre otomatik kategorilendir
- `full_X.md` + `X.md` çiftlerinde **full_X'i** koru (daha eksiksiz)
- Tanınmayan prefix'ler → `misc/uncategorized/` (sonra elle)
- Türkçe karakterler için normalize et: `unicodedata.normalize('NFKD', s).encode('ASCII','ignore')`

### 3. Batch Taşıma
```python
for src_name in files:
    kategori = determine_category(src_name)
    hedef = os.path.join(skills_dir, kategori, src_name)
    os.makedirs(os.path.dirname(hedef), exist_ok=True)
    shutil.move(src, hedef)
```

### 4. Dedup (Duplicate Temizleme)
```python
# full_X.md + X.md varsa → full_X.md korunur, X.md silinir
by_basename = defaultdict(list)
for f in files:
    base = f[5:] if f.startswith('full_') else f
    is_full = f.startswith('full_')
    by_basename[base].append((f, is_full))
# Her grupta full_ varsa onu koru
```

### 5. `_2.md` Duplicate Temizleme
Bulk move sırasında hedef dosya zaten varsa `shutil.move()` otomatik olarak `_2.md` soneki ekler. Bunlar sonradan temizlenmeli:

```python
# Move sonrası _2.md dosyalarını tara
for root, dirs, files in os.walk(skills_dir):
    for f in files:
        if f.endswith('_2.md'):
            original = f.replace('_2.md', '.md')
            original_path = os.path.join(root, original)
            dup_path = os.path.join(root, f)
            if os.path.exists(original_path):
                # İçerik aynıysa sil, farklıysa merge et
                os.remove(dup_path)
```

## DB Onarım & Konsolidasyon

Batch işlemler sırasında karşılaşılan DB sorunları ve çözümleri:

### FTS5 Bozulması (vtable constructor failed)

**Belirti:** `OperationalError: vtable constructor failed: <tablo_adi>`
**Sebep:** FTS5 virtual table bozulmuş (disk image malformed)

**Çözüm:**
```python
# 1) Back up broken DB
os.rename(broken_db, broken_db + '.corrupted')

# 2) Rebuild from source using good copy of data
conn_good = sqlite3.connect(good_source_db)
cg = conn_good.cursor()
cg.execute("SELECT ad, aciklama, icerik, kaynak FROM beceriler")

conn_new = sqlite3.connect(broken_db)
cn = conn_new.cursor()
cn.execute("CREATE VIRTUAL TABLE skill_fts USING fts5(ad, aciklama, icerik, kaynak, tokenize='unicode61')")

for row in cg.fetchall():
    cn.execute("INSERT INTO skill_fts (ad, aciklama, icerik, kaynak) VALUES (?, ?, ?, ?)", row)
conn_new.commit()

# 3) Verify
cn.execute("SELECT COUNT(*) FROM skill_fts")  # Should match source
cn.execute("PRAGMA integrity_check")           # Must be 'ok'
```

### Hermes Profile state.db (11MB profile DB)

**Konum:** `~/AppData/Local/hermes/profiles/reymen/state.db`  
**Tablo:** `messages` (role, content, timestamp), `sessions`, `schema_version`

Bu DB Hermes ajanının ana state'idir — **proje DB'si DEĞİL**, profil DB'sidir. Farklı yerde olduğu için unutulmaya müsait:

```python
STATE = os.path.expanduser(r'~/AppData/Local/hermes/profiles/reymen/state.db')

conn = sqlite3.connect(STATE)
c = conn.cursor()
# messages tablosu -> role: user/assistant/tool
c.execute("SELECT rowid, role, content FROM messages")
for row in c.fetchall():
    rid, role, content = row
    if role == 'user':
        ne, kim = 'kullanici_mesaji', 'kullanici'
    elif role == 'assistant':
        ne, kim = 'ajan_yaniti', 'reymen'
    else:
        ne, kim = 'tool_cagrisi', 'sistem'
    c.execute("UPDATE messages SET ne=?, nerede=?, nasil=?, neden=?, kim=? WHERE rowid=?",
              (ne, 'hermes', 'otomatik', 'kayit', kim, rid))
```

**Uyarı:** state.db Hermes tarafından canlı kullanılır. `ALTER TABLE` tehlikeli olabilir — önce yedek al, sonra dene.

### DB Senkronizasyonu (Multi-Location)

Aynı içerikli DB'ler projede farklı dizinlerde bulunabilir:

| Dizin | DB |
|:------|:---|
| `.ReYMeN/skills_index.db` | Ana kopya (birincil) |
| `reymen/cereyan/.ReYMeN/skills_index.db` | İkincil kopya |

**Belirti:** Aynı isimde DB'ler farklı kayıt sayısına sahip (örn. 5781 vs 2206)

**Çözüm:**
1. Birincil kopyayı belirle (genelde `.ReYMeN/` altındaki daha güncel)
2. İkincilden eksik kayıtları birincile merge et
3. Birincildeki tüm veriyi ikincile kopyala (senkronizasyon)
4. Her ikisinde de `PRAGMA integrity_check` yap

```python
# Merge: secondary -> primary
for row in secondary_rows:
    primary_cursor.execute("SELECT COUNT(*) FROM beceriler WHERE ad=?", (row[0],))
    if primary_cursor.fetchone()[0] == 0:
        primary_cursor.execute("INSERT INTO ...", row)

# Sync: primary -> secondary
secondary_cursor.execute("DELETE FROM beceriler")
for row in primary_rows:
    secondary_cursor.execute("INSERT INTO ...", row)
```

### Çift Skills Index (Duplicate DB Consolidation)

**Belirti:** Projede aynı içerikli 2 skills_index.db var, farklı sayıda kayıt

**Çözüm:**
```python
# 1) Primary'de olmayan kayıtları secondary'den merge et
cs.execute("SELECT ad, aciklama, icerik, kaynak FROM beceriler")
for row in cs.fetchall():
    cp.execute("SELECT COUNT(*) FROM beceriler WHERE ad=?", (row[0],))
    if cp.fetchone()[0] == 0:
        cp.execute("INSERT INTO beceriler (ad, aciklama, icerik, kaynak) VALUES (?, ?, ?, ?)", row)

# 2) Secondary'yi primary ile senkronize et (tam kopya)
cs.execute("DELETE FROM beceriler")
cp.execute("SELECT ad, aciklama, icerik, kaynak FROM beceriler")
for row in cp.fetchall():
    cs.execute("INSERT INTO beceriler (ad, aciklama, icerik, kaynak) VALUES (?, ?, ?, ?)", row)
conn_sec.commit()

# 3) Her ikisinde de integrity check yap
```

### FTS5 Virtual Table'a 5N1K Kolon Ekleme

FTS5 tabloları **ALTER TABLE desteklemez**. Ayrı bir mapping tablosu oluştur:

```sql
CREATE TABLE IF NOT EXISTS beceriler_5n1k (
    rowid INTEGER PRIMARY KEY,
    ne TEXT DEFAULT '',
    nerede TEXT DEFAULT '',
    nasil TEXT DEFAULT '',
    neden TEXT DEFAULT '',
    kim TEXT DEFAULT ''
);
INSERT INTO beceriler_5n1k (rowid, ne, nerede, nasil, neden, kim)
SELECT rowid, 'genel', 'genel', 'skill', 'ogrenme', 'reymen' FROM beceriler;
```

### Genel DB Sağlık Kontrolü

```python
conn = sqlite3.connect(db_path)
c = conn.cursor()
c.execute("PRAGMA integrity_check")
# 'ok' gelmezse → DB bozuk

c.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = c.fetchall()
for tbl in tables:
    cn = conn.cursor()
    cn.execute(f'SELECT COUNT(*) FROM "{tbl[0]}" LIMIT 1')  # Check accessibility
# Herhangi bir hata → tablo bozuk
```

Memory (ogrenmeler.db) kayıtlarını 5N1K'ya göre sınıflandırmak için:

### 5N1K Taksonomisi

| N | Anlamı | Ana Başlıklar (Örnek) |
|:-:|:-------|:----------------------|
| **NE** | Konu/Kategori | ai/ecc, windows/terminal, guvenlik, kod, medya |
| **NEREDE** | Platform/Konum | windows/local, kali/vm, hermes/profil, telegram |
| **NASIL** | Yöntem | otomatik, video_ogrenme, web_aramasi, hata_cozumu |
| **NEDEN** | Sebep | otomasyon, guvenlik, test_dogrulama, ogrenme |
| **KIM** | Kaynak | reymen, windows_ajani, video_ajani, kullanici |

### Uygulama Adımları
```python
# 1. DB analizi
# 2. Keyword-based classification
# 3. Heuristic matching (prefix, suffix, Turkish norm)
# 4. DB update with new columns (ne, nerede, nasil, neden, kim)
# 5. Final pass for remainders
```

### Known Pitfalls
- **Türkçe karakterler**: `ı, ş, ğ, ü, ö, ç` → `unicodedata.normalize('NFKD', ...)` ile ASCII'ye çevir
- **full_X + X duplicate**: `full_3d-pipeline.md` + `3d-pipeline.md` — full_ olanı koru
- **Boş kategori**: `ecc---` gibi bozuk formatları temizle (`---` → `/`, `_` → `/`)
- **"Diğer" kalıntısı**: Son kalan 1-5 kayıt genelde Türkçe karakterli veya çok kısa. Elle müdahale gerek.
- **FTS5 Virtual Table**: skills_index.db gibi FTS5 tabloları ALTER TABLE desteklemez. Çözüm: ayrı bir `_5n1k` mapping tablosu oluştur (`CREATE TABLE beceriler_5n1k (rowid, ne, nerede, ...)`)
- **ogrenme.db vs ogrenmeler.db**: Projede `ogrenme.db` (reymen/hafiza/) ve `ogrenmeler.db` (cereyan/.ReYMeN/) AYRI DB'lerdir. Birini sınıflandırmak diğerini etkilemez. Her ikisi de ayrı ayrı işlenmeli.
- **`_2.md` kalıntıları**: Bulk move sırasında hedef dosya varsa otomatik `_2.md` eklenir. Move sonrası mutlaka tara ve temizle.

## Format Zorunluluğu (Kullanıcı Tercihi)

5N1K sonuç ağacını **şu formatta** göster. Kullanıcı bu kalıbı ısrarla istiyor:

```
📊 5N1K — ANA BASLIKLAR ve ALT BASLIKLAR

NE (Konu/Kategori)
├── 🧩 ecc                 392
├── 🤖 AI                  160  (ML:160)
├── 🌐 Ağ                  137
├── 💻 Kod                 104
├── 🎨 Yaratıcı             84
├── 🪟 Windows              84
├── 📏 degerlendirme        66
├── 📺 Medya                63
├── 💬 prompt               51
├── 📝 nlp                  49
├── 🧪 Test                 48
├── 🔥 inference            42
├── 🧠 training             41
├── 🔒 Güvenlik             38
├── 🤖 ajan                 32
├── 🏛 mimari               30
├── 🔄 cicd                 25
├── 🔌 mcp                  21
├── 💻 software             19  (patterns:19)
├── 🔍 denetim              19
├── 📊 veri                 11
├── 🛡 ai-guvenlik          11
├── 👁 goruntu              10
├── ... ve N baslik daha
```

Emoji + hiyerarşik ağaç + pipe table. Alternatif format kullanma.

## İstatistik Formatı

Batch sonrası özet:
```
📊 SONUÇ:
├── ✅ İşlenen:    2176 dosya
├── 📂 Kategori:   34 klasör
├── 🗑️ Silinen:    1079 duplicate
├── ❌ Hata:       0
└── ⏱️ Süre:       45sn
```

## Referanslar
- [5N1K Memory Taksonomisi](references/5n1k-taxonomy.md) — Detaylı memory sınıflandırma kılavuzu
- `.ReYMeN/memory_taxonomy_5n1k.md` — Projede canlı taksonomi dokümanı
- `reymen-hafiza-oncelikli-akis` skill'inde sessiz onay entegrasyonu
