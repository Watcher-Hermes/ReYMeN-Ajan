---
name: env-kayit-kurallari
title: "Env Kayit Kurallari"
tags: [automation, windows]
description: Use FIRST before any configuration, API key, or settings task. Contains all .env file locations, key names, and the rule that .env is the single source of truth. Every .env change must be saved to Obsidian automatically. Check this skill before reading/writing any config.
version: 1.0.0
author: marko
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [env, config, api-key, token, obsidian, kayit, oncelik, source-of-truth, kalici]
audience: user
related_skills: [obsidian-vault-kurallari, tam-sistem-yetkisi, obsidian]
---

# .env Kayıt Kuralları — Öncelik ve Kalıcı Hafıza

## KURAL 1 — .env İLK KONTROL YERİDİR

Herhangi bir ayar, API anahtarı veya token gerektiğinde:
```
1. ÖNCE .env dosyasını oku
2. Sonra config.yaml'a bak
3. En son SOUL.md'e bak
```

**HİÇBİR ZAMAN** token/key değerini başka yerden tahmin etme veya hard-code etme.

---

## .env Dosya Konumları (KESİN)

```
ReYMeN Agent .env (CLI):
  C:\Users\marko\AppData\Local\hermes\.env

ReYMeN Gateway .env (ÖNCELİKLİ — gateway burayı okur):
  C:\Users\marko\.hermes\.env          (*~/.hermes/.env)
  NOT: Gateway her zaman önce ~/.hermes/.env'yi okur.
       AppData/.env'deki ayarlar buraya da kopyalanmalıdır.
       Yoksa oluşturulmalıdır.

hermes.py (özel sistem) .env:
  C:\Users\marko\hermes-ai\.env

hermes-ai yapılandırma:
  C:\Users\marko\AppData\Local\hermes\config.yaml
```

Obsidian yansımaları (maskeli, güncel):
```
C:\Users\marko\OneDrive\Belgeler\Obsidian Vault\ReYMeN\env-hermes-agent.md
C:\Users\marko\OneDrive\Belgeler\Obsidian Vault\ReYMeN\env-hermes-ai.md
```

---

## ReYMeN Agent .env — Anahtar Listesi

| Anahtar | Açıklama |
|---------|---------|
| `TELEGRAM_BOT_TOKEN` | Telegram bot bağlantısı |
| `TELEGRAM_ALLOWED_USERS` | İzinli kullanıcı ID'leri (NOT: `ALLOWLIST` değil, `ALLOWED_USERS`) |
| `GATEWAY_ALLOW_ALL_USERS` | `true` yapılırsa gateway tüm kullanıcılara izin verir (yedek) |
| `DEEPSEEK_API_KEY` | DeepSeek / Nous erişim |
| `NOUS_API_KEY` | Nous Portal API |
| `GOOGLE_API_KEY` | Google AI / Gemini |
| `GEMINI_API_KEY` | Gemini (Google_API_KEY ile aynı) |
| `OBSIDIAN_VAULT_PATH` | `C:\Users\marko\OneDrive\Belgeler\Obsidian Vault` |
| `TERMINAL_TIMEOUT` | Terminal komut zaman aşımı (saniye) |

## hermes-ai .env — Anahtar Listesi

| Anahtar | Değer |
|---------|-------|
| `DEEPSEEK_API_KEY` | DeepSeek / Nous API |
| `OBSIDIAN_VAULT` | `C:\Users\marko\OneDrive\Belgeler\Obsidian Vault` |
| `OLLAMA_MODEL` | `dolphin-llama3` |
| `OLLAMA_BASE_URL` | `http://localhost:11434` |

---

## KURAL 2 — .env Değişince Obsidian'a Yaz

Her `.env` değişikliğinden sonra şu komutu çalıştır:

```bash
"C:\Users\marko\hermes-ai\venv\Scripts\python.exe" "C:\Users\marko\hermes-ai\env_watcher.py"
```

Veya arka planda sürekli izle:
```bash
# Arka planda calistir (Ctrl+C ile durdur)
"C:\Users\marko\hermes-ai\venv\Scripts\python.exe" "C:\Users\marko\hermes-ai\env_watcher.py"
```

---

## KURAL 3 — .env Okuma (Python)

```python
import os
from pathlib import Path
from dotenv import load_dotenv

# ReYMeN Agent .env
load_dotenv(r"C:\Users\marko\AppData\Local\hermes\.env")

# Değeri oku
token = os.getenv("TELEGRAM_BOT_TOKEN", "")
key   = os.getenv("DEEPSEEK_API_KEY", "")
vault = os.getenv("OBSIDIAN_VAULT_PATH", "")

print(f"Token: {token[:10]}***")
print(f"Vault: {vault}")
```

---

## KURAL 4 — .env Yazma (Python)

```python
import re
from pathlib import Path

def set_env(env_path: str, key: str, value: str) -> None:
    p    = Path(env_path)
    text = p.read_text(encoding="utf-8") if p.exists() else ""
    pat  = re.compile(rf"^{re.escape(key)}\s*=.*", re.MULTILINE)
    new  = f"{key}={value}"
    if pat.search(text):
        text = pat.sub(new, text)
    else:
        text = text.rstrip("\n") + f"\n{new}\n"
    p.write_text(text, encoding="utf-8")
    print(f"[OK] {key} yazildi")

# Kullanim:
set_env(
    r"C:\Users\marko\AppData\Local\hermes\.env",
    "TELEGRAM_BOT_TOKEN",
    "yeni_token_buraya"
)
```

---

## KURAL 5 — Obsidian'daki env Notları

Obsidian'da şu dosyalar her zaman güncel olmalı:

- `[[env-hermes-agent]]` — Ana ReYMeN anahtarları (maskeli)
- `[[env-hermes-ai]]` — hermes.py anahtarları (maskeli)

Bu notlar `env_watcher.py` tarafından otomatik güncellenir.
Değerlerin tamamını görmek için gerçek `.env` dosyasını oku.

---

## Hangi .env Neyi Etkiler

```
TELEGRAM_BOT_TOKEN    → hermes gateway, Telegram mesajları
TELEGRAM_ALLOWED_USERS → gateway yetkilendirme (NOT: ALLOWLIST değil)
GATEWAY_ALLOW_ALL_USERS → gateway acil durum bypass'ı
OBSIDIAN_VAULT_PATH   → skill sync, not yazma (DOGRU YOL)
DEEPSEEK_API_KEY      → DeepSeek / Nous model erişimi
NOUS_API_KEY          → Nous Portal (stepfun/step-3.7-flash:free modeli)
GOOGLE_API_KEY        → Gemini modelleri
OLLAMA_MODEL          → Yerel model (dolphin-llama3)
KLING_ACCESS_KEY      → Kling AI video (kling.ai/dev/api-key)
KLING_SECRET_KEY      → Kling AI secret
RUNWAYML_API_KEY      → RunwayML video (key_ + 128 hex = 132 char)
```

**ÖNEMLİ:** Gateway Scheduled Task ile çalışıyorsa `~/.hermes/.env` dosyası da oluşturulmalı. Aksi halde gateway allow ayarlarını görmez ve tüm kullanıcıları unauthorized olarak reddeder.

## Common Pitfalls

1. **config_guard.py scripti yok** — `~/.hermes/scripts/config_guard.py` dosyası oluşturulmalı. İçeriği: env dosyalarını tarar, placeholder/boş değerleri bulur, tutarlılık kontrolü yapar. `--fix` ile otomatik düzeltme, `--report` ile detaylı rapor. Script yoksa cron job başarısız olur.
2. **env_watcher.py çalışmıyor** — Docstring'de `\\\\\\\\U` escape hatası; `env_watcher.py` update edildi.
2. **Yanlış vault yolu** — `OBSIDIAN_VAULT_PATH` her zaman `OneDrive\\\\Belgeler\\\\Obsidian Vault`.
3. **ReYMeN maskeleme + env_watcher token bozma** — ReYMeN `read_file`, `cat` gibi araçlarla `.env` okunduğunda değerleri maskeler (`***`). Eğer bu maskelenmiş içerik `env_watcher.py` tarafından `.env`'ye geri yazılırsa, tüm token'lar bozulur. **Belirti**: `.env`'de `TELEGRAM_BOT_TOKEN=851817***9aM` gibi satırlar olması. **Çözüm**:
   - Token değişikliği sonrası env_watcher'ı çalıştırma
   - `.env` okumak için `Path(env_path).read_bytes()` (binary mode) kullan, `read_file` veya `cat` kullanma
   - Gerçek içeriği doğrulamak için: `python -c "with open(r'.env','rb') as f: print(f.read().decode())"`
4. **GITHUB_TOKEN bozulduysa** — `.env`'yi manuel düzelt veya yeniden yaz. ReYMeN'in maskelenmiş değerini kopyalayıp yapıştırma — her zaman orijinal token'ı kullan.
5. **Key bulunamıyor** — Önce doğru `.env` dosyasını `load_dotenv()` ile yüklediğinden emin ol.
6. **.env değişti ama Obsidian güncel değil** — `env_watcher.py` başlatılmamış olabilir.
7. **Gateway env adı farkı:** Gateway `TELEGRAM_ALLOWED_USERS` bekler. Eğer `.env`'de `TELEGRAM_ALLOWLIST` yazıyorsa gateway onu görmez ve tüm kullanıcıları unauthorized olarak reddeder. Gateway "connected" gösterir ama mesaj işlemez. **Çözüm:** Her zaman `TELEGRAM_ALLOWED_USERS` kullan, `TELEGRAM_ALLOWLIST` veya başka varyant değil.
9. **~/.hermes/.env yoksa gateway allow ayarlarını görmez:** Gateway başlarken önce `~/.hermes/.env`'yi okur. Bu dosya yoksa ana `.env`'deki ayarlar da çalışmaz. Dosyayı oluştur ve içine en azından `GATEWAY_ALLOW_ALL_USERS=true` veya `TELEGRAM_ALLOWED_USERS=...` yaz. Bu dosya Scheduled Task ile çalışan gateway için gereklidir.
10. **.env'ye yazarken f-string + *** SyntaxError:** Python f-string içinde `***` kullanmak SyntaxError'a yol açar (`f-string: expressions nested too deeply`). Çözüm: string concatenation veya normal format() kullan:
    ```python
    # YANLIŞ
    content += f'API_KEY=value={secret}'

    # DOĞRU — string concatenation
    content += 'API_KEY='
    content += secret
    content += '\n'

    # Veya heredoc
    python3 << 'PYEOF'
    path = r'path\to\.env'
    with open(path, 'a') as f:
        f.write(f'KEY=val...')
    PYEOF
    ```

11. **KRİTİK: Key Drift — Farklı .env Dosyalarında Farklı Key'ler:**
    - **Sorun:** Gateway `~/.hermes/.env`'yi okur, ReYMeN proje `.env`'yi okur. Farklı key'ler kullanılırsa kredi boşa harcanır!
    - **Belirti:** Platform'da kredi hızlı düşer ama siz sadece birkaç test yapmışsınızdır.
    - **Çözüm:** `config_guard.py` ile periyodik kontrol:
      ```bash
      python ~/.hermes/scripts/config_guard.py --fix
      ```
    - **Önleme:** Tüm .env dosyalarındaki XIAOMI_API_KEY aynı olmalı.

12. **Xiaomi MiMo API Doğru Yapılandırma (2026-06-24 güncellendi):**
    - **Base URL:** `https://api.xiaomimimo.com` (token-plan-sgp değil!)
    - **Header (pay-as-you-go):** `Authorization: Bearer $KEY`
    - **Header (token-plan):** `api-key: $KEY`
    - **DOĞRU Model adı:** `mimo-v2-pro` ✅ (API'de böyle görünür)
    - **YANLIŞ Model adı:** `mimo-v2.5` ❌ (API'de YOK, 404 hatası verir!)
    - **Key formatı:** `sk-...` (51 karakter)
    - **Ucuz model:** `mimo-v2-pro` ($0.14/M input, $0.28/M output)
    - **Pahalı model:** `mimo-v2.5-pro` ($0.435/M input, $0.87/M output)
    - **Doğrulama:** `curl https://api.xiaomimimo.com/v1/models` ile listede var mı kontrol et

13. **Token Tasarrufu — Sohbet Geçmişini Kısıtla:**
    - **Sorun:** Her mesaj tüm geçmişi içerir → 50 mesaj = 75K token
    - **Çözüm:** `MAX_GECMIS_UZUNLUGU = 20` ile son 20 mesaj
    - **Tasarruf:** ~%60 token tasarrufu
    - **Yapılandırma:** `~/.hermes/config.yaml`'a compression ekle:
      ```yaml
      compression:
        enabled: true
        threshold: 0.85
        summary_model: "deepseek-chat"
      ```

## KURAL 6 — .env Doğrulama ve Denetim

Her `.env` değişikliği sonrası veya periyodik olarak doğrulama yap:

### Adım 1: Dosya Konumlarını Tara
```bash
# Hermes profilleri
find /c/Users/marko/AppData/Local/hermes -name "*.env" -type f

# Proje içi .env'ler
find /c/Users/marko/Desktop/Reymen\ Proje/hermes_projesi -name "*.env" -type f
```

### Adım 2: Her Dosyayı Kontrol Et
```python
import os
from pathlib import Path

def validate_env(env_path: str) -> list[str]:
    """ .env dosyasını doğrula, sorunları listele """
    issues = []
    p = Path(env_path)
    
    if not p.exists():
        return [f"Dosya bulunamadı: {env_path}"]
    
    content = p.read_text(encoding="utf-8")
    lines = content.strip().split("\n")
    
    for i, line in enumerate(lines, 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        
        if "=" not in line:
            issues.append(f"Satır {i}: Eşittir işareti eksik: {line}")
            continue
        
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        
        # Boş değer kontrolü
        if not value:
            issues.append(f"Satır {i}: Boş değer: {key}")
        
        # Bozuk format kontrolü (yanlış escape, eksik tırnak)
        if value.count("'") % 2 != 0 or value.count('"') % 2 != 0:
            issues.append(f"Satır {i}: Eksik tırnak: {key}={value}")
        
        # Placeholder kontrolü
        if value in ["***", "xxx", "your_key_here", "secret...xxxx"]:
            issues.append(f"Satır {i}: Yer tutucu değer: {key}={value}")
    
    return issues
```

### Adım 3: .env.example ile Karşılaştır
```python
def compare_with_example(env_path: str, example_path: str) -> list[str]:
    """ .env ile .env.example'ı karşılaştır, eksik anahtarları bul """
    missing = []
    
    def extract_keys(path: Path) -> set[str]:
        if not path.exists():
            return set()
        keys = set()
        for line in path.read_text(encoding="utf-8").split("\n"):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key = line.split("=", 1)[0].strip()
                keys.add(key)
        return keys
    
    env_keys = extract_keys(Path(env_path))
    example_keys = extract_keys(Path(example_path))
    
    for key in example_keys - env_keys:
        missing.append(f"Eksik anahtar: {key}")
    
    return missing
```

### Adım 4: Çoklu Konum Tutarlılığı
```python
def check_consistency(base_env: str, profile_envs: list[str]) -> list[str]:
    """ Ana .env ile profillerdeki .env'ler arasındaki tutarsızlıkları bul """
    inconsistencies = []
    
    def read_keys(path: str) -> dict[str, str]:
        result = {}
        p = Path(path)
        if not p.exists():
            return result
        for line in p.read_text(encoding="utf-8").split("\n"):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                result[key.strip()] = value.strip()
        return result
    
    base_keys = read_keys(base_env)
    
    for profile_env in profile_envs:
        profile_keys = read_keys(profile_env)
        for key in base_keys:
            if key in profile_keys and base_keys[key] != profile_keys[key]:
                if base_keys[key] != "***" and profile_keys[key] != "***":
                    inconsistencies.append(
                        f"{Path(profile_env).name}: {key} "
                        f"farklı değer ('{base_keys[key]}' vs '{profile_keys[key]}')"
                    )
    
    return inconsistencies
```

### Doğrulama Komutları
```bash
# Tüm .env'leri listele
find /c/Users/marko -name "*.env" -type f 2>/dev/null

# Belirli bir .env'yi doğrula
python -c "
from pathlib import Path
p = Path('C:/Users/marko/AppData/Local/hermes/.env')
for i, line in enumerate(p.read_text().split('\n'), 1):
    if '=' in line and not line.startswith('#'):
        key, _, val = line.partition('=')
        status = '✅' if val.strip() else '❌ BOŞ'
        print(f'{i:2d}. {status} {key.strip()}')
"

# Hızlı tutarsızlık kontrolü
diff <(grep -E "^[A-Z_]+=" /c/Users/marko/AppData/Local/hermes/.env | sort) \
     <(grep -E "^[A-Z_]+=" /c/Users/marko/AppData/Local/hermes/profiles/kiral38/.env | sort)
```

## Verification Checklist

- [ ] `C:\Users\marko\AppData\Local\hermes\.env` okunabildi
- [ ] `TELEGRAM_BOT_TOKEN` boş değil
- [ ] `OBSIDIAN_VAULT_PATH` doğru yolu gösteriyor
- [ ] Obsidian'da `env-hermes-agent.md` güncel timestamp'e sahip
- [ ] `env_watcher.py` arka planda çalışıyor (veya elle tetiklendi)
- [ ] Tüm .env dosyalarında bozuk satır yok
- [ ] Eksik anahtarlar (.env.example ile karşılaştırıldı)
- [ ] Farklı profillerdeki değerler tutarlı
