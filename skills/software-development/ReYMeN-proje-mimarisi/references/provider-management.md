# ReYMeN Provider Yönetim Rehberi

## Provider Ekleme/Kaldırma Workflow'u

ReYMeN'de bir provider (DeepSeek, Xiaomi, xAI, Groq vb.) eklemek veya kaldırmak için **4+ dosyada koordineli değişiklik** gerekir.

### Dosya Haritası

| # | Dosya | Değişiklik | Konum |
|---|-------|-----------|-------|
| 1 | `.env` | API key ekle/kaldır | `hermes_projesi/.env` |
| 2 | `startup_ekrani.py` | Menü listesinden çıkar (2 yer) | `hermes_projesi/startup_ekrani.py` |
| 3 | `baslangic_kontrol.py` | 3 haritadan çıkar | `reymen/sistem/baslangic_kontrol.py` |
| 4 | `config.yaml` | fallback_providers listesinden çıkar | `~/.hermes/config.yaml` |

### Detay: startup_ekrani.py (2 Değişiklik)

**1. `_BULUT_ENV` sözlüğü (satır ~350):**
```python
_BULUT_ENV = {
    "deepseek": ("DEEPSEEK_API_KEY", "deepseek-v4-flash", "DeepSeek"),
    "xiaomi":   ("XIAOMI_API_KEY", "mimo-v2-pro", "Xiaomi (ucuz)"),
    # KALDIRILACAK provider buradan silinir
}
```

**2. `provider_goster` sözlüğü (satır ~470):**
```python
provider_goster = {
    "deepseek": "DeepSeek",
    "xiaomi": "Xiaomi (ucuz)",
    # KALDIRILACAK provider buradan silinir
}.get(provider, provider or "Yerel")
```

### Detay: baslangic_kontrol.py (3 Harita)

**1. `_BULUT_ENV_MAP` (sınıf içinde, ~satır 168):**
```python
_BULUT_ENV_MAP = {
    "deepseek": "DEEPSEEK_API_KEY",
    "xiaomi": "XIAOMI_API_KEY",
    # KALDIRILACAK provider
}
```

**2. `_BULUT_MODELLER` (~satır 294):**
```python
_BULUT_MODELLER = {
    "deepseek": [("deepseek-chat", "DeepSeek Chat")],
    "xiaomi": [("mimo-v2-pro", "MiMo V2 Pro (ucuz)")],
    # KALDIRILACAK provider
}
```

**3. `_BULUT_ENV` (~satır 305):**
```python
_BULUT_ENV = {
    "deepseek": "DEEPSEEK_API_KEY",
    "xiaomi": "XIAOMI_API_KEY",
    # KALDIRILACAK provider
}
```

### Detay: .env

```env
# KALDIRILACAK provider'ın key'i silinir
XAI_API_KEY=xai-...  # ← Bu satır silinir
```

### Detay: config.yaml

```yaml
fallback_providers:
  - provider: xiaomi
    model: mimo-v2-pro
  # KALDIRILACAK provider bu listeden çıkarılır
```

---

## Pitfall: Patch Sonrası Indentation Hatası

**Sorun:** Sözlük entry'si silerken `_BULUT_ENV = {` satırı da kazayla silinebilir.

**Örnek hata:**
```python
    # Sadece entry silindi, { satırı gitti → IndentationError
    "deepseek": ("DEEPSEEK_API_KEY", ...),
```

**Çözüm:** Patch yaparken `old_string`'e sözlüğün açılış satırını dahil et:
```python
# DOĞRU:
old_string = '_BULUT_ENV = {\n        "deepseek":'
new_string = '_BULUT_ENV = {\n        "deepseek":'  # { korunur

# YANLIŞ:
old_string = '"deepseek":'  # { satırı unutuldu
```

---

## Pitfall: Eski Yorum Satırı Kalması

**Sorun:** Provider silindikten sonra eski yorum satırlarında hala o provider'ın adı kalabilir.

**Çözüm:** `grep -n "provider_adi"` ile tüm dosyalarda tarama yap, kalan referansları temizle.

---

## Xiaomi MiMo API Doğruları (2026-06-24)

| Alan | Doğru Değer | Yanlış (Eski) |
|------|-------------|---------------|
| Base URL | `https://api.xiaomimimo.com` | `https://api.minimax.chat/v1` |
| Model adı | `mimo-v2-pro` | `mimo-v2.5-pro` |
| Fiyat | $0.000036/M token (girdi) | — |
| Key formatı | `sk-s5m...` | — |

**Not:** Xiaomi API'sinde `mimo-v2.5-pro` diye bir model yok. Doğru adı `mimo-v2-pro`.

---

## Provider Sıralama Kuralı

Kullanıcı "paralı modelleri kaldır" dediğinde:
1. DeepSeek ve Xiaomi kalır (kullanıcının belirttiği modeller)
2. xAI, Groq, OpenAI, Anthropic vb. kaldırılır
3. LM Studio (yerel, ücretsiz) her zaman en sonda kalır

**Varsayılan fallback zinciri (paralı modeller kaldırıldıktan sonra):**
```
DeepSeek (deepseek-v4-flash) → Xiaomi (mimo-v2-pro) → LM Studio (yerel)
```

---

## Kontrol Listesi

Her provider değişikliği sonrası:
- [ ] `grep -rn "provider_adi" --include="*.py" --include="*.env" --include="*.yaml"` ile tüm referansları tara
- [ ] `__pycache__` temizle: `find . -name "__pycache__" -not -path "./venv/*" -exec rm -rf {} +`
- [ ] Import test: `python -c "import reymen; print('OK')"`
- [ ] `.env`'de tekrarlayan yorum satırlarını temizle
