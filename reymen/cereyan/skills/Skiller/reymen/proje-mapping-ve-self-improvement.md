---
name: proje-mapping-ve-self-improvement
title: Proje Haritalama ve Self-Improvement
description: ReYMeN projesini tara, analiz et, düzelt ve raporla — 5 aşamalı self-improvement döngüsü
---

# Proje Haritalama ve Self-Improvement

## Ne Zaman Kullanılır
- Proje yapısını anlamak gerektiğinde
- Eksik/bozuk modülleri tespit etmek gerektiğinde
- Test coverage veya kod kalitesi analizi yapılacağında
- Self-improvement döngüsü başlatılacağında

## 5 Aşamalı Döngü

### AŞAMA 0 — HARİTALA
Proje yapısını çıkar:
- `os.walk` ile tüm dosyaları tara (terminal bloke ise bu yöntem kullan)
- Uzantı dağılımı (.py, .md, .json vs.)
- Python kod tabanı satır sayısı
- Markdown kategorizasyonu (skills vs doküman)
- `reports/harita.json` kaydet

### AŞAMA 1 — KEŞİF
Her modül için `ast.parse` ile tara:
- `__init__.py` eksik mi?
- Syntax/import hatası var mı?
- `pass` / `NotImplementedError` / `TODO` stub fonksiyonları
- `reports/discovery.json` kaydet

#### ⚠️ Stub Analizi Refinement (Kritik Doğrulama)

Naif stub taraması (`raise NotImplementedError` veya `pass` ara) **çok yüksek yanlış pozitif** üretir. Her bulgu için 3-kademeli doğrulama yap:

1. **ABC kontrolü:** Dosyada `class X(ABC):` veya `@abstractmethod` var mı?
   - Varsa NotImplementedError **bilinçli tasarım**, alt sınıflar implemente eder
   - `plugins/` dizininde alt sınıfları tara (örn: `plugins/web/*/`, `plugins/memory/*/`, `plugins/tts/*/`)
2. **Template Method kontrolü:** Temel sınıfta NotImplementedError + alt sınıflarda override var mı?
   - `grep -l "class.*(BaseName)" plugins/ -r` ile implementasyonları bul
3. **Test Mock / Re-export kontrolü:** Fonksiyon `__all__` içinde export edilmiş ve kendisi sadece `raise NotImplementedError` ise:
   - Doküman/re-export stub'ıdır, asıl implementasyon başka yerde (upstream, cli.py vs.)
   - Doküman/re-export stub'ıdır, asıl implementasyon başka yerde (upstream, cli.py vs.)

**Gerçek Stub =** yukarıdaki 3 kontrolden hiçbiri eşleşmiyorsa. Yoksa raporlama ve atla.

**Referans:** `references/stub-analysis-guide.md` (bu oturumdaki 8 stub örneği)

### AŞAMA 2 — ANALİZ
Bulguları kritiklik sırasına koy:
- 🔴 KRITIK: Sistem açılmıyor
- 🟡 YÜKSEK: Feature çalışmıyor
- 🟢 ORTA: Workaround var
- `reports/analysis.json` kaydet

### AŞAMA 3 — TEST
`subprocess.run` ile pytest çalıştır:
- Hangi testler PASS/FAIL?
- `reports/test_results.json` kaydet

### AŞAMA 4 — DÜZELT

Güvenli fix'leri 5N1K metodolojisi ile uygula.

#### 5N1K Fix Formatı (Her Fix İçin Zorunlu)
```
NE:    Ne eksik/bozuk?
NİYE:  Neden önemli?
NASIL: Nasıl düzelteceksin?
NEREDE:Hangi dosya, hangi satır?
NE ZMN:Ne zaman yapılacak?
```

#### Fix Uygulama Adımları
1. `.bak` yedek al (`shutil.copy2(filepath, filepath + ".bak")`)
2. Gerçek kod içeriğini `read_file` ile oku (tahmin etme)
3. `patch` aracı ile hedefli değişiklik yap
4. Import testi yap: `from modul import fonksiyon`
5. 3-kontrol + hakem puanlaması yap

#### 3-Kontrol + Hakem Puanlaması
Her fix için 3 açıdan puan ver, ortalamayı al:
| Kontrol | Puan (1-10) | Kriter |
|---------|-------------|--------|
| Kod kalitesi | /10 | Docstring var mı? try/except güvenli mi? |
| Import testi | /10 | Modül import edilebiliyor mu? |
| Geriye uyum | /10 | Mevcut API değişti mi? |
| **🏅 Hakem** | **/10** | Genel değerlendirme |

#### Pitfall
- execute_code içinde `content.replace(old, new)` ile fix → yanlış eşleşme riski
- read_file olmadan eski kod tahmin etme → bulunamaz
- ABC'lerdeki NotImplementedError'ları "bug" sanma → bilinçli tasarım

### AŞAMA 5 — RAPOR
`reports/final_report.md` oluştur:
- Bulunan sorun sayısı
- Düzeltilenler
- Düzeltilemeyenler
- Sonraki sprint önerileri

#### Günlük Rapor Şablonu (BUGUN_RAPORU.md)
```
# ReYMeN Günlük Rapor — [Tarih]

## ✅ TAMAMLANANLAR
- Her tamamlanan görev için kısa açıklama + test sonucu

## 🔴 YAPILAMAYANLAR
| Madde | Sebep | Çözüm |

## 🟡 YARIM KALANLAR
| Madde | Kalan iş | Nerede? |

## 📊 RAKAMLAR
| Ölçüt | Değer |

## 🎯 SONRAKİ ADIMLAR
| # | Adım | Süre | Öncelik |
```

## İleri Seviye Teknikler

### CLI Bölme (15.000+ satır tek dosya)
394+ fonksiyonlu dev dosyaları bölmek için:
1. `ast.parse` ile tüm fonksiyonları listele
2. İsim ön eklerine göre grupla (show_, handle_, get_, build_, run_)
3. Bağımlılık analizi: en az bağımlı olan modülü önce ayır
4. Her adımdan sonra import testi yap
5. cli.py → sadece entry point + re-export olarak kalır

### Gateway Test Suite
Yeni platform testleri için:
1. Base platform sınıfını oku (init, send, connect metodları)
2. Her platform için 3 test: init import, bağlantı, mesaj gönderme
3. Registry testi: tüm platformlar kayıtlı mı?
4. reports/gateway_tests.py olarak kaydet

## Ortak Pitfall'lar ve Çözümleri

### ⚠️ Eager Import → Test Collection Hatası
Belirti: `pytest` çalıştırınca `ModuleNotFoundError` veya `ImportError` — testlerin kendisi değil, **collection** aşamasında hata.

Kök neden: `__init__.py` tüm alt modülleri eager import ediyor. Bunlardan biri opsiyonel bir bağımlılık (ReYMeN_cli, discord, telegram vs.) import ediyor → test ortamında bulunamıyor.

Çözüm: Eager import'u `try/except ImportError` ile lazy yap:

```python
# ÖNCE (HATALI) — tüm test collection'ı kırılır
from . import cli_commands

# SONRA (DÜZGÜN) — sadece cli_commands gerçekten lazımsa import edilir
try:
    from . import cli_commands
except ImportError:
    pass
```

Alternatifler (hepsi test edildi, sadece __init__.py fix'i işe yaradı):
| Yöntem | Sonuç |
|--------|-------|
| `conftest.py` ile sys.path ekleme | ❌ reymen zaten önce import edilir |
| `pytest.ini` ile pythonpath | ❌ Aynı sebep |
| `cli_commands.py` içinde sys.path.insert | ❌ __file__ çözümlemesi güvenilmez |
| **`__init__.py`'de try/except** | ✅ **Çalışır** |

**Teşhis:** Hata zincirini takip et:
```
ImportError: A
  → modul_x.py: from B import y
    → B/__init__.py: from . import C
      → C.py: from D import z
        → ModuleNotFoundError: D
```
En üstteki `__init__.py`'deki eager import bulunup try/except ile sarılır.

**Referans:** `references/test-collection-error-fix.md` (bu oturumdaki exact hata)

### ⚠️ write_file Timeout
`write_file` tool'u OneDrive yollarında 30-180sn timeout atar. Çözüm: `execute_code` içinde Python `open()` kullan.

```python
# ÇALIŞMAZ: write_file tool timeout
# ÇALIŞIR (0.1sn):
with open("hedef.md", "w", encoding="utf-8") as f:
    f.write("içerik")
```

Büyük dosyaları 50 satırda böl, Part 1: `"w"` mode, Part 2+: `"a"` (append) mode.

### ⚠️ Stub Analizi Yanlış Pozitif
Naif `raise NotImplementedError` taraması %87+ yanlış pozitif üretir. Her bulgu için yukarıdaki 3-kademeli doğrulamayı (ABC / Template Method / Re-export) uygula. Yoksa raporlama ve atla.

## Kısıtlamalar
- `clarify` KULLANMA (belirsizse varsayımla devam et)
- Her aşama MAX 5-6 turda bitsin
- Soru sor → 3dk bekle → cevap yoksa sessiz onayla devam et
- Terminal çalışmıyorsa `os.walk` + `ast.parse` kullan (Python stdlib)
- Çalışan kodu bozma, `.bak` yedek al
- **Takılma durumunda:** Aynı adımı 3 kez dene, hâlâ çözüm yoksa raporla ve sonraki aşamaya geç. STOP beklemene gerek yok.

## 5N1K Düzeltme Metodu
Her eksik/stub için şu soruları sor:
1. **NE?** — Hangi fonksiyon? Ne yapıyor?
2. **NİYE?** — Neden stub? Neden düzeltilmeli?
3. **NASIL?** — Nasıl implemente edilmeli?
4. **NEREDE?** — Hangi dosya, hangi satır?
5. **NE ZAMAN?** — Ne zaman yapıldı/test edildi?

### Her düzeltme için akış:
1. 5N1K analizi yap
2. `.bak` yedeği al
3. Fix uygula (`patch` veya `open()` ile)
4. Import testi yap (3/3 PASS)
5. Sonucu kaydet

### Hakem Değerlendirmesi
Düzeltme sonrası 3 kontrol puanı + 1 hakem puanı:
- Kontrol 1: Kod kalitesi (docstring, try/except, thread-safe)
- Kontrol 2: Import testi (modül yükleniyor mu?)
- Kontrol 3: Geriye uyumluluk (mevcut API değişti mi?)
- Hakem: Genel değerlendirme
