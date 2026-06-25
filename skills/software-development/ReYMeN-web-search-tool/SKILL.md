---
name: ReYMeN-web-search-tool
category: software-development
version: 1.0.0
description: ReYMeN projesine web_search_tool.py ekleme ve motor.py'ye kaydetme adimlari
tags: [skill, hermes, ReYMeN, web-search]
---

# ReYMeN-web-search-tool

ReYMeN projesine DuckDuckGo web arama tool'u ekler.

## Dosyalar

| Dosya | Yol |
|-------|-----|
| web_search_tool.py | `tools/web_search_tool.py` |
| motor.py kaydı | `motor.py` → `_plugin_moduller_yukle()` listesine **tools.web_search_tool** eklenir |

## Test

```bash
python -m py_compile tools/web_search_tool.py
python -c "from tools.web_search_tool import run; print(run('Python dili', 'duckduckgo'))"
```

## API

```
WEB_ARAMA("sorgu", "duckduckgo")
  -> DuckDuckGo'da ara, ozet don
```

## ⚠️ PITFALL: Prompt Enjeksiyonu + Hallüsinasyon (2026-06-25)

Web arama sonuçlarını sistem promptuna eklerken **3 kritik kural**:

### 1. ASLA çift ekleme
PromptBuilder'da web sonuçları hem formatlı hem raw JSON olarak eklenirse model kafası karışır.
```
❌ parcalar.append(formatli_web_sonucu)  # formatlı
❌ parcalar.append(f"## Ek Bilgi\n{json.dumps(baglam)}")  # raw JSON TEKRAR
✅ parcalar.insert(0, formatli_web_sonucu)  # SADECE bir kez, EN ÜSTE
```

### 2. Anti-hallüsinasyon kuralları
"Bilmiyorum DEME" talimatı modeli uydurmaya zorlar. Bunun yerine koşullu kurallar kullan:
```
✅ "Web sonucu varsa kullan, yoksa 'elimde güncel veri yok' de"
✅ "Asla uydurma fiyat/veri/tarih verme"
❌ "'Bilmiyorum', 'gerçek zamanlı verilere erişimim yok' DEME"  # uydurmaya zorlar
```

### 3. Hızlı yol tuzağı
`?` içeren sorular hızlı yola giderse web araması atlanır. Güncel kelime tespiti ile ReAct'e düşür:
```python
GUNCEL_KELIMELER = ["fiyat", "altın", "bitcoin", "hava", "haber", "döviz", "borsa", ...]
if any(k in mesaj for k in GUNCEL_KELIMELER):
    tip = "karmasik"  # ReAct'e düş, web araması yap
```

### İlgili dosyalar
| Dosya | Değişiklik |
|-------|-----------|
| `reymen/arac/prompt_builder.py` | `insert(0)` + raw JSON tekrarı kaldırıldı |
| `reymen/cereyan/conversation_loop.py` | Anti-hallüsinasyon kuralları |
| `reymen/sistem/main.py` | Hızlı yol güncel kelime tespiti |
