---
name: reymen-model-switcher
description: Otomatik model/provider geçiş sistemi — API key bitince tüm Telegram botları otomatik olarak yeni modele geçer.
---

# ReYMeN Model Switcher

## When to Use
API key kredisi bittiğinde, provider başarısız olduğunda, veya manuel model değişikliği gerektiğinde. KATI KURAL: ReYMeN hangi modeldeyse TÜM Telegram botları da aynı modelde.

## Problem
API key bitince ReYMeN hata veriyor ama Telegram botları eski modelde kalıyor. Kullanıcı manuel müdahale etmek zorunda.

## Çözüm: model_switcher.py

### Provider Fallback Zinciri
```python
PROVIDER_ZINCIRI = [
    {"ad": "xiaomi", "model": "mimo-v2.5-pro", "oncelik": 1},
    {"ad": "deepseek", "model": "deepseek-chat", "oncelik": 2},
    {"ad": "openai", "model": "gpt-4o-mini", "oncelik": 3},
    {"ad": "lmstudio", "model": "local-model", "oncelik": 4},
    {"ad": "ollama", "model": "llama3", "oncelik": 5},
]
```

### Akış
1. `api_key_kontrol()` — key var mı?
2. `api_key_bitti_mi()` — test isteği gönder (402/401 → bitmiş)
3. `en_iyi_provider_bul()` — fallback zincirinden ilk çalışan
4. `config_guncelle()` — config.json + .env güncelle
5. `bot_config_kaydet()` — TÜM botlara aynı model ata (KATI KURAL)
6. `gateway_yeniden_baslat()` — gateway process restart
7. `_baglanti_testi()` — Telegram bot getMe ile test

### API Key Bitiş Tespiti
```python
# Basit test isteği
url = provider["api_url"] + "/chat/completions"
payload = {"model": provider["model"], "messages": [{"role": "user", "content": "test"}], "max_tokens": 5}
# 402 → Payment Required → kredi bitmiş
# 401 → Unauthorized → key geçersiz
# 429 → Rate limit → geçici, sonraki provider'a geçme
```

### Dosyalar
- `reymen/sistem/model_switcher.py` — Ana modül
- `.ReYMeN/model_state.json` — Geçiş geçmişi
- `.ReYMeN/bot_config.json` — Bot yapılandırması

### Kullanım
```python
from reymen.sistem.model_switcher import ModelSwitcher
switcher = ModelSwitcher()

# Otomatik kontrol + geçiş
sonuc = switcher.kontrol_ve_gec()

# Manuel geçiş
sonuc = switcher.manuel_gec("deepseek")

# Durum raporu
print(switcher.formatla())
```

## Pitfalls

- **LM Studio/Ollama key gerektirmez** — `api_key_env=None` olarak işaretle, `_servis_kontrol()` ile ping at
- **429 Rate Limit** — geçici hata, provider değiştirme, retry yap
- **Gateway restart** — Windows'ta `CREATE_NO_WINDOW` flag'i ile subprocess.Popen kullan
- **Bot token eşleşme** — `.env`'deki `TELEGRAM_BOT_TOKEN_*` pattern'ini regex ile bul

## 5N1K

| Alan | Açıklama |
|:-----|:---------|
| Kim | ReYMeN Agent operatörü |
| Ne | Otomatik model/provider geçişi |
| Nerede | `reymen/sistem/model_switcher.py` |
| Ne Zaman | API key bittiğinde veya provider başarısız olduğunda |
| Neden | Bot kesintisini önlemek |
| Nasıl | Fallback zinciri + config güncelleme + gateway restart |
