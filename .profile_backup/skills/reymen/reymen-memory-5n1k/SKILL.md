---
name: reymen-memory-5n1k
description: 5N1K metodolojisi ile hafıza DB'lerini sınıflandırma ve organize etme
title: "ReYMeN Memory 5N1K Taksonomisi"
version: 2.0.0
tags: [memory, taxonomy, 5n1k, classification, db]
---

# ReYMeN Memory 5N1K Taksonomisi

## Ne Zaman Kullanılır
- Yeni bir `.db` hafıza dosyası keşfedildiğinde
- Mevcut hafıza kayıtlarının kategorize edilmesi gerektiğinde
- Veri tutarlılığı/entegrasyon kontrolü yapılırken
- DB bozulması tespit edildiğinde

## 5N1K Kolonları
Her kayda şu 5 kolon eklenir:

| Kolon | Anlamı | Örnek Değerler |
|:------|:-------|:---------------|
| `ne` | Konu/Kategori | ecc, AI/ML, Ağ, Kod, Windows, güvenlik, test |
| `nerede` | Platform/Konum | windows, kali, hermes, github, telegram |
| `nasil` | Yöntem | test, otomatik, video_ogrenme, web_arama |
| `neden` | Sebep | ogrenme, hata_cozumu, otomasyon, test |
| `kim` | Kaynak | reymen, windows_ajani, kali_ajani, video_ajani, kullanici |

## Hedef DB'ler (Konumlar)

| DB | Konum | Tablo | Tür |
|:---|:------|:------|:----|
| ogrenmeler.db | `reymen/cereyan/.ReYMeN/` | ogrenmeler | Regular table |
| hafiza.db | `reymen/cereyan/.ReYMeN/` | kayitlar | Regular + FTS5 |
| skills_index.db | `.ReYMeN/` + `reymen/cereyan/.ReYMeN/` | beceriler | **FTS5 only** |
| skill_index.db | `.ReYMeN/` | skill_fts | **FTS5 only** |
| ogrenme.db | `reymen/hafiza/` | ogrenmeler | Regular table |
| hatalar.db | `reymen/hafiza/` | hatalar | Regular table |
| state.db | `~/AppData/Local/hermes/profiles/reymen/` | messages, sessions | Regular table |
| session.db | `.ReYMeN/` | ajan_gunlugu | **FTS5 only** |
| memory_fts.db | `.ReYMeN/` | hafiza | **FTS5 only** |

**Önemli:** `skills_index.db` aynı anda 2 yerde var (`.ReYMeN/` ve `reymen/cereyan/.ReYMeN/`). Veri ayrışabilir. Sınıflandırma öncesi hangisinin birincil olduğunu belirle.

## Sınıflandırma Adımları

### 1. Analiz
```python
# DB yapısını kontrol et
c.execute("PRAGMA table_info(tablo_adi)")
c.execute("SELECT COUNT(*) FROM tablo_adi")
c.execute("PRAGMA integrity_check")
```

### 2. Kolon Ekle
```python
for col in ['ne', 'nerede', 'nasil', 'neden', 'kim']:
    try:
        c.execute(f"ALTER TABLE tablo ADD COLUMN {col} TEXT DEFAULT ''")
    except:
        pass  # zaten var
```

### 3. Keyword Eşleme
Anahtar kelimelere göre `ne` (NE) kategorisi belirlenir:

| Kategori | Tetikleyici Kelimeler |
|:---------|:----------------------|
| `ecc` | ecc\_, edge case, classification |
| `AI/ML` | mlops\_, model, training, inference, llm |
| `Ağ` | nmap, netstat, ipconfig, port, network |
| `Kod` | software-development, code, python, git |
| `Windows` | windows, terminal, automation, system |
| `Yaratıcı` | creative, ascii, excalidraw, design |
| `Güvenlik` | security, guvenlik, pentest, firewall |
| `ajan` | agent, claude, codex, otonom |
| `test` | test, benchmark, evaluation |
| `devops` | devops, docker, backup, cron |
| `cicd` | ci/cd, deploy |
| `mcp` | mcp, powerbi |
| `mimari` | architecture, transformer, attention |
| `inference` | inference, vllm, sampling |
| `training` | training, fine-tune, lora, rlhf |
| `degerlendirme` | eval, benchmark, lm-eval |
| `prompt` | prompt |
| `nlp` | ner, nli, sentiment, tokenizer |
| `veri` | data, preprocessing, vectorization |
| `goruntu` | vision, vlm, vit |
| `denetim` | audit, compliance, regulatory |
| `cicd` | ci/cd, deploy, pipeline |
| `Medya` | media, video, audio, youtube |
| `Verimlilik` | productivity, workflow |
| `Kullanıcı` | user-preferences, tercih, profil |

### 4. Alt Başlıklar
Büyük kategoriler (30+ kayıt) ana başlığa yükseltilebilir:
- `ai/ecc` → `ecc` (392)
- `ai/prompt` → `prompt` (51)
- `ai/nlp` → `nlp` (49)
- `ai/inference` → `inference` (42)
- `ai/training` → `training` (41)
- `ai/agents` → `ajan` (32)
- `ai/architecture` → `mimari` (30)
- `ai/evaluation` → `degerlendirme` (66)
- `devops/cicd` → `cicd` (25)
- `security/audit` → `denetim` (19)

### 5. Diğer Alanlar
```python
# NEREDE
if 'kali' in text: nerede = 'kali'
elif 'windows' in text: nerede = 'windows'
elif 'telegram' in text: nerede = 'telegram'

# NASIL
if 'test' in text or 'eval' in text: nasil = 'test'
elif 'video' in text or 'youtube' in text: nasil = 'video_ogrenme'

# KIM
if 'kali' in text: kim = 'kali_ajani'
elif 'windows' in text: kim = 'windows_ajani'
else: kim = 'reymen'
```

## Çıktı Formatı
```
📊 5N1K — ANA BAŞLIKLAR ve ALT BAŞLIKLAR

NE (Konu/Kategori)
├── 🧩 ecc                 392
├── 🤖 AI/ML               160
├── 🌐 Ağ                  137
├── 💻 Kod                 104
├── 🪟 Windows              84
├── 🎨 Yaratıcı             84
├── 📏 degerlendirme        66
├── 💬 prompt               51
├── 📝 nlp                  49
├── 🔥 inference            42
├── 🧠 training             41
├── 🔒 Güvenlik             38
├── 🤖 ajan                 32
├── 🏛 mimari               30
├── 🔄 cicd                 25
├── 🔌 mcp                  21
└── ... ve devami
```

## Merkezi Memory DB (Konsolidasyon Hedefi)

Tüm 10 DB, `reymen/cereyan/.ReYMeN/memory.db`'de tek DB'de birleştirilmiştir:

```sql
CREATE TABLE memory (
    id INTEGER PRIMARY KEY,
    kaynak TEXT,           -- orijinal DB adı (ogrenmeler, hafiza, state, ...)
    ne TEXT DEFAULT '',    -- 5N1K: ana başlık
    alt_ne TEXT DEFAULT '',-- 5N1K: alt başlık
    nerede TEXT DEFAULT '',
    nasil TEXT DEFAULT '',
    neden TEXT DEFAULT '',
    kim TEXT DEFAULT '',
    baslik TEXT DEFAULT '',-- özet satırı
    icerik TEXT DEFAULT '',-- tam içerik
    guven REAL DEFAULT 0.0,
    tarih TEXT DEFAULT '',
    etiket TEXT DEFAULT ''
);

-- FTS5 arama indeksi
CREATE VIRTUAL TABLE memory_fts USING fts5(baslik, icerik);
```

**Sorgulama:**
```python
conn = sqlite3.connect("reymen/cereyan/.ReYMeN/memory.db")
c = conn.cursor()
# NE başlığına göre
c.execute("SELECT baslik, icerik FROM memory WHERE ne=? AND alt_ne=?", (ana_baslik, alt_baslik))
# FTS5 full-text arama
c.execute("SELECT baslik, ne, alt_ne FROM memory_fts WHERE memory_fts MATCH ?", ("port tarama",))
```

**Konsolidasyon akışı:** `toplu-islem-yonetimi` skill'inde "Çift Skills Index" ve "FTS5 Virtual Table'a 5N1K Kolon Ekleme" bölümlerine bak.

## Pitfall'lar
- **FTS5 tabloları ALTER edilemez** → ayrı bir `_5n1k` tablosu oluştur
- **Transaction içinde transaction** → DELETE zaten implicit transaction açar, BEGIN kullanma
- **Sütun adı farklılıkları** → Her DB'nin farklı kolon adı olabilir (`rowid` vs `id`)
- **Türkçe karakterler** → Direkt karakter mapping kullan. NFKD normalize **KULLANMA** (ASCII'ye çevirirken `ı→i`, `ğ→g` dönüşümü bozulur, "yaratıcı" → "yaratc" olur):
  ```python
  # DOĞRU: Direkt mapping
  for tr, en in [('ü','u'),('ö','o'),('ı','i'),('ğ','g'),('ş','s'),('ç','c')]:
      text = text.replace(tr, en)
  ```
- **Case sensitivity** → Tüm `ne` değerleri `LOWER()` ile normalize edilmelidir
- **Integrity kontrolü** → Her işlem öncesi PRAGMA integrity_check yap

## Test
```python
c.execute("SELECT ne, COUNT(*) FROM tablo GROUP BY ne ORDER BY COUNT(*) DESC")
c.execute("SELECT COUNT(*) FROM tablo WHERE ne='Diğer' OR ne=''")
```
