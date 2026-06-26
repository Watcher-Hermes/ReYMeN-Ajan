---
name: reymen-auto-web-search
description: Otomatik web arama + doğrulama entegrasyonu — LLM'in güncel bilgi gerektiren sorularda otomatik web araması yapar, sonucu doğrular, doğrulanırsa LLM'i atlar.
---

# ReYMeN Otomatik Web Arama Entegrasyonu

## When to Use
LLM "bilmiyorum" diyor ama güncel bilgi gerektiren soru soruluyorsa (fiyat, hava, haber, döviz). Bu kalıcı çözüm 3 katmanlı koruma sağlar.

## Problem
LLM (mimo-v2.5, DeepSeek vb.) kendi eğitim verisiyle cevap veriyor. "altın ons fiyatı" sorulduğunda "gerçek zamanlı verilere erişimim yok" diyor. Oysa web arama aracı var, ama otomatik tetiklenmiyor.

## Çözüm: 4 Katmanlı Koruma

### Katman 1 — Sistem Promptu (`conversation_loop.py`)
`_sistem_promptu_olustur()` fonksiyonuna ZORUNLU web arama kuralları ekle:
```
"Bilmiyorum" deme. web_search_tool kullan.
Fiyat/hava/haber sorgularında MUTLAKA web_search_tool ile ara.
```

### Katman 2 — Otomatik Tetikleyici (`auto_web_search.py`)
`run_conversation()` fonksiyonunda, kullanıcı mesajı geldiğinde:
1. `AutoWebSearch.web_arasi_mi(hedef)` ile kontrol et
2. Güncel bilgi tetikleyici kelime varsa (fiyat, bugün, şu an, hava, haber) → web araması yap
3. Sonucu `baglam["web_arama_sonucu"]` olarak ekle

### Katman 3 — Web Sonucu Doğrulama (YENİ)
Web araması yapıldıktan sonra sonucun güncel olup olmadığını doğrula:
1. Yıl 2026 var mı? (+30 puan)
2. "canlı", "anlık", "bugün" gibi tazelik ifadesi var mı? (+25)
3. Bugünün tarihi var mı? (+30)
4. Sayısal veri var mı? (+15)
5. Eski yıl var mı? (-15)

**Puanlama:** ≥30 → ✅ Doğrulandı | 15-29 → ⚠️ Şüpheli, yeniden ara | <15 → ❌ Güncel değil

### Katman 4 — LLM Atlama (YENİ)
Web sonucu doğrulanırsa LLM'i tamamen atla, direkt web verisini dön:
```python
if guncel_mi:
    return {"yanit": sonuc_metni, "kaynak": "web_arama_dogrulanmis", "turlar": 0}
# LLM hiç çağrılmadı → hallüsinasyon riski = 0
```

Doğrulanamazsa → farklı sorguyla tekrar ara (`_yeniden_ara()`):
```python
zengin_sorgular = [f"{sorgu} 2026", f"{sorgu} güncel", f"bugün {sorgu}"]
```

### Katman 3 — Prompt'a Web Sonucu Ekleme
`_sistem_promptu_olustur()` fonksiyonunda:
```python
if baglam and baglam.get("web_arama_sonucu"):
    prompt += f"\nGUNCEL WEB ARAMA SONUCLARI:\n{baglam['web_arama_sonucu']}\n"
    prompt += "YUKARIDAKI sonuclari kullanarak guncel bilgi ver.\n"
```

## Tetikleyici Kelimeler

| Kategori | Kelimeler |
|:---------|:----------|
| Zaman | bugün, şu an, şimdi, güncel, son, latest, today, now |
| Finans | fiyat, kur, dolar, euro, bitcoin, altın, borsa |
| Hava | hava, durumu, weather |
| Haber | haber, news, deprem, maç, skor |

## Web Gerektirmeyen (ATLA)
merhaba, selam, nasılsın, teşekkür, python, kod, script, dosya, hafıza, ayar

## Dosyalar
- `reymen/arac/web_search_tool.py` — DuckDuckGo/Brave/SearXNG arama motoru
- `reymen/cereyan/auto_web_search.py` — 5 tetikleyicili otomatik kontrol
- `reymen/cereyan/conversation_loop.py` — `run_conversation()` + `_sistem_promptu_olustur()` entegrasyonu

## Pitfalls

- **DuckDuckGo rate limit** — DDG bazen 429 döner, Brave API key varsa öncelikli kullan
- **Türkçe karakter** — `web_search()` fonksiyonuna `dil="tr"` parametresi eklenmeli
- **Prompt boyutu** — Web sonucu prompt'a eklenince token artar, max 3 sonuç ile sınırlandır
- **Cache** — Aynı sorgu 24 saat içinde tekrar sorulursa web araması yapma
- **⚠️ Değişken sıralama hatası (KRİTİK)** — `sonuc` dict'i try bloğundan ÖNCE tanımlanmalı. Tanımlanmadan kullanılırsa `NameError` → except yutuyor → web araması hiç yapılmamış gibi davranıyor.
- **⚠️ DDG snippet cache (KRİTİK)** — DDG arama sonuçları snippet'leri ÖNBELLEKTEN gelir. Fiyat/kur sorgularında snippet eski veri gösterebilir (3.978 TL ama gerçek fiyat 3.993 TL). Çözüm: ilk sonucun URL'sine HTTP GET yap, sayfadan regex ile canlı fiyat çek (`_sayfadan_fiyat_cek()`). Pattern: `reymen/arac/web_search_tool.py` → `_sayfadan_fiyat_cek()`. Detay: `references/live-data-extraction.md`
- **⚠️ LLM dejenerasyonu (CJK spam)** — mimo-v2.5 bazen aynı token'ı (因为因为因为...) yüzlerce kez tekrarlar. Çözüm: `_cikti_dogrula()` ile çıktı doğrulama — tek karakter 20+ tekrar, kelime 5+ tekrar, CJK spam (>10 karakter), max 4000 karakter limiti. `conversation_loop.py`'de text yanıt handler'ına ekle.
- **⚠️ Bozuk skill dosyaları** — Skills klasöründeki bozuk .md dosyaları (yarım JSON, drift_duzeltme referansları) LLM'i sonsuz döngüye sokabilir. `usage_count` > 10 ve `REFERANS_ARA` gibi tool call kalıpları içeren dosyaları `_corrupted_backup/`'a taşı. Düzenli temizlik yap.
- **⚠️ Kullanıcı doğrulama isteği** — Kullanıcı "haklısın" demeden önce veriyi doğrula. Fiyat karşılaştırırken en az 2 kaynak kullan, aradaki farkı açıkla. "Snippet cache'ten dolayı ~15 TL fark" gibi.

## Verification
```python
from reymen.cereyan.auto_web_search import AutoWebSearch
aws = AutoWebSearch()
assert aws.web_arasi_mi("altın ons fiyatı") == (True, "...")
assert aws.web_arasi_mi("merhaba") == (False, "...")
```
