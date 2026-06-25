# 5N1K Memory Taksonomisi Referansı

> **Kullanım:** `ogrenmeler.db` (1773), `hafiza.db` (2462), `skills_index.db` (2206) — toplam 6876 kayıt  
> **DB Kolonları:** `ne`, `nerede`, `nasil`, `neden`, `kim`  
> **Durum:** 3 DB de sınıflandırıldı, 0 uncategorized  
> **Güncelleme:** 2026-06-21

---

## 5N1K Nedir?

| Harf | Anlamı | Örnek Değerler |
|:----:|:-------|:---------------|
| **NE** | Konu/Kategori | ecc, AI/ML, windows/automation, kod, prompt |
| **NEREDE** | Platform/Konum | windows/hermes/kali/github/powerbi |
| **NASIL** | Yöntem | otomatik/video_ogrenme/web_aramasi/hata_cozumu |
| **NEDEN** | Sebep | otomasyon/guvenlik/test/ogrenme/kurulum |
| **KIM** | Kaynak/Kişi | reymen/kali_ajani/windows_ajani/video_ajani/hermes |

---

## NE (Konu) — 55 Ana Başlık

### İlk 30 (en yüksekten itibaren)

| # | NE | Adet | Açıklama |
|:-:|:---|:----:|:---------|
| 1 | `ecc` | 392 | Edge Case Classification (yükseltildi) |
| 2 | `AI` | 160 | AI/ML genel |
| 3 | `Ağ` | 137 | Network, nmap, netstat |
| 4 | `Kod` | 104 | Yazılım geliştirme |
| 5 | `Yaratıcı` | 84 | Tasarım, ASCII, media |
| 6 | `Windows` | 84 | Windows sistem/otomasyon |
| 7 | `degerlendirme` | 66 | Benchmark, evaluation (yükseltildi) |
| 8 | `Medya` | 63 | Video, ses, görsel |
| 9 | `prompt` | 51 | Prompt mühendisliği (yükseltildi) |
| 10 | `nlp` | 49 | Doğal dil işleme (yükseltildi) |
| 11 | `Test` | 48 | Test & benchmark |
| 12 | `DevOps` | 44 | CI/CD, deployment |
| 13 | `inference` | 42 | Model inference (yükseltildi) |
| 14 | `training` | 41 | Model eğitimi (yükseltildi) |
| 15 | `Guvenlik` | 38 | Güvenlik |
| 16 | `Verimlilik` | 35 | Productivity |
| 17 | `ajan` | 32 | Ajan sistemleri (yükseltildi) |
| 18 | `mimari` | 30 | AI mimarisi (yükseltildi) |
| 19 | `katalog` | 29 | Katalog dosyaları |
| 20 | `Kullanici` | 28 | Kullanıcı tercihleri |
| 21 | `cicd` | 25 | CI/CD (yükseltildi) |
| 22 | `mcp` | 21 | MCP protokolü (yükseltildi) |
| 23 | `software` | 19 | Yazılım pattern'leri |
| 24 | `denetim` | 19 | Audit/Security denetim (yükseltildi) |
| 25 | `Sistem` | 14 | Sistem yönetimi |
| 26 | `veri` | 11 | Veri işleme (yükseltildi) |
| 27 | `ai-guvenlik` | 11 | AI güvenlik (yükseltildi) |
| 28 | `goruntu` | 10 | Görüntü işleme (yükseltildi) |
| 29 | `research` | 8 | Araştırma |
| 30 | `gaming` | 8 | Oyun |

### Tam Liste (55 başlık)

| NE | Adet | NE | Adet | NE | Adet |
|:---|---:|:---|---:|:---|---:|
| ecc | 392 | AI | 160 | Ağ | 137 |
| Kod | 104 | Yaratici | 84 | Windows | 84 |
| degerlendirme | 66 | Medya | 63 | prompt | 51 |
| nlp | 49 | Test | 48 | DevOps | 44 |
| inference | 42 | training | 41 | Guvenlik | 38 |
| Verimlilik | 35 | ajan | 32 | mimari | 30 |
| katalog | 29 | Kullanici | 28 | cicd | 25 |
| mcp | 21 | software | 19 | denetim | 19 |
| Sistem | 14 | veri | 11 | ai-guvenlik | 11 |
| goruntu | 10 | research | 8 | medya | 8 |
| gaming | 8 | reymen | 7 | is-akisi | 5 |
| veri-bilimi | 4 | multimodal | 4 | github | 4 |
| Egitim | 4 | uyum | 3 | tor | 3 |
| misc | 3 | media | 3 | urun | 2 |
| llm | 2 | hafiza | 2 | devops | 2 |
| calisma-tezgahi | 2 | android | 2 | ag | 2 |
| voice | 1 | sosyal-medya | 1 | smart-home | 1 |
| scaling | 1 | red-team | 1 | powerbi | 1 |
| hermes | 1 | cross-platform | 1 | | |

### Alt Başlıklar (25 adet)

| Ana Başlık | Alt | Adet | Ana Başlık | Alt | Adet |
|:-----------|---:|:---|---:|:---|:---:|
| AI | ML | 160 | software | patterns | 19 |
| medya | apple | 6 | medya | video | 2 |
| reymen | hafiza | 2 | reymen | karsilastirma | 1 |
| reymen | karar | 1 | reymen | format | 1 |
| reymen | cozum | 1 | powerbi | mcp | 1 |
| media | video | 3 | urun | planlama | 2 |
| ag | tarama | 2 | | | |

---

## DB'ye 5N1K Kolon Ekleme

### Normal Tablo (ogrenmeler.db, hafiza.db)
```sql
ALTER TABLE tablo_adi ADD COLUMN ne TEXT DEFAULT '';
ALTER TABLE tablo_adi ADD COLUMN nerede TEXT DEFAULT '';
ALTER TABLE tablo_adi ADD COLUMN nasil TEXT DEFAULT '';
ALTER TABLE tablo_adi ADD COLUMN neden TEXT DEFAULT '';
ALTER TABLE tablo_adi ADD COLUMN kim TEXT DEFAULT '';
```

### FTS5 Virtual Table (skills_index.db) ⚠️
FTS5 tabloları ALTER TABLE desteklemez. **Ayrı bir tablo** oluştur:
```sql
CREATE TABLE IF NOT EXISTS beceriler_5n1k (
    rowid INTEGER PRIMARY KEY,
    ne TEXT DEFAULT '',
    nerede TEXT DEFAULT '',
    nasil TEXT DEFAULT '',
    neden TEXT DEFAULT '',
    kim TEXT DEFAULT ''
);
-- INSERT INTO beceriler_5n1k SELECT rowid, ... FROM beceriler
```

---

## Kategorilendirme Algoritması

```python
import unicodedata, sqlite3

def norm(s):
    return unicodedata.normalize('NFKD', s).encode('ASCII','ignore').decode().lower()

# Strateji sırası:
# 1) Prefix eşleşmesi (ecc_, mlops_, creative_, ...)
# 2) Keyword eşleşmesi (nmap, netstat, windows, ...)
# 3) Dosya adı ilk kelime
# 4) misc/uncategorized (son çare, < %1 olmalı)

CLASS_RULES = {
    'yaratici': ['creative_','ascii','excalidraw','p5js','sketch','baoyu'],
    'kod': ['software-development_','python','javascript','react','django'],
    'windows/otomasyon': ['windows-automation_','ekran-al','mouse-klavye'],
    'ajan': ['autonomous-ai-agents_','claude','codex','opencode','hermes-agent'],
}

# Önce prefix matrisinde ara
for cat, keywords in CLASS_RULES.items():
    for kw in keywords:
        if kw.lower() in text:
            ne = cat
            break

# Sonra bozuk formatları temizle (--- → /, _ → /)
UPDATE ogrenmeler SET kategori = REPLACE(REPLACE(kategori, '---', '/'), '_', '/')
```

## Sınıflandırma Sonrası Format

5N1K ağacını **bu formatta** göster (kullanıcı ısrarla bu formatı istiyor):
```
📊 5N1K — ANA BAŞLIKLAR ve ALT BAŞLIKLAR

NE (Konu/Kategori)
├── 🧩 ecc                 392
├── 🤖 AI                  160  (ML:160)
├── 🌐 Ağ                  137
├── 💻 Kod                 104
├── 🎨 Yaratıcı             84
├── 🪟 Windows              84
...
```

Emoji + pipe table + tree formatı. Başka format kullanma.
