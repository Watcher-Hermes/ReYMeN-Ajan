---
skill_id: env-corruption-runtime-lock
usage_count: 1
last_used: 2026-06-23
---

## .env Corruption Recovery & Runtime Lock Çözümü

> **Olay:** Kiral38 bot token değişti, .env kurtarma ve multi-profil runtime lock çözümü
> **Tarih:** 23 Haziran 2026

### 1. .env Corruption Recovery

`.env` dosyası şu yollarla bozulabilir (hepsi yaşandı):

| Hata | Sebep | Sonuç |
|:-----|:------|:------|
| `write_file` ile placeholder yazmak | Token'ı `885848...**` yazdım | Token literal `***` oldu |
| `sed -i "s|8774151638:***|8858482950:***|"` | `***` sistem redaksiyonu, gerçek değer değil | sed hiçbir şey yapmadı |
| `echo 'TELEGRAM_BOT_TOKEN=***` | Token'ı düz metin yazdım | Diğer env değişkenleri kayboldu |
| `cp reymen/.env kiral38/.env` | Kopyalama doğru ama token yanlış | API key'ler doğru, token yanlış |

#### ✅ Doğru .env Kurtarma Yöntemi

**Python ile binary-safe token replacement (tek güvenilir yöntem):**

```python
import os

env_path = os.path.expanduser("~/AppData/Local/hermes/profiles/<profil>/.env")
# Referans dosyadan oku (ör: reymen profilinden)
ref_path = os.path.expanduser("~/AppData/Local/hermes/profiles/reymen/.env")

with open(ref_path, 'rb') as f:
    ref_content = f.read()

# Eski token'ı yenisiyle değiştir (byte-level, redaksiyon yok)
old_token = b'8774151638:AAFNMVK12XjC-V7TLIM98WGmQgd4KRF72tU'
new_token = b'8858482950:AAFkQ-7f4dE_njD4JEJGSGNpnhSqW80uvJY'

new_content = ref_content.replace(old_token, new_token, 1)

with open(env_path, 'wb') as f:
    f.write(new_content)
```

**Doğrulama (od -c ile):**
```bash
grep "TELEGRAM" ~/AppData/Local/hermes/profiles/<profil>/.env | od -c | head -6
# Beklenen: TELEGRAM_BOT_TOKEN=8858482950:AAFkQ-... (gerçek token karakterleri)
# Hatalı:   TELEGRAM_BOT_TOKEN=* * * \n (literal asterisk)
```

### 2. Global Runtime Lock (Multi-Profil Kilidi)

Hermes gateway, **global** bir runtime lock kullanır: `~/AppData/Local/hermes/gateway.lock`

Bu lock, **tüm profiller arasında paylaşılır**. Yani:
- `reymen` gateway çalışıyorken → `kiral38` gateway **BAŞLATILAMAZ**
- `kiral38` gateway çalışıyorken → `reymen` gateway **BAŞLATILAMAZ**

**Hata mesajı:**
```
ERROR gateway.run: Gateway runtime lock is already held by another instance. Exiting.
```

#### Kilit Tipleri

| Lock Dosyası | Kapsam | Etki |
|:-------------|:-------|:-----|
| `~/AppData/Local/hermes/gateway.lock` | **Global** — tüm profiller | Runtime lock, sadece 1 gateway çalışabilir |
| `~/AppData/Local/hermes/profiles/<name>/gateway.lock` | **Profil** — o profile özel | PID+lock dosyası |
| `~/AppData/Local/hermes/profiles/<name>/gateway.pid` | **Profil** — PID kaydı | Stale PID referansı |

#### Zombie Lock Temizleme

Gateway **ölmüş** ama lock dosyası kalmışsa:

```bash
# 1. Önce process'in gerçekten öldüğünü doğrula
ps -p <PID> 2>&1 | grep -v "PID_NOT_FOUND" || echo "PID_OLMUS"

# Not: git-bash'de ps -p false negative verebilir (Windows process'lerini görmez)
# O zaman şu alternatifleri dene:
tasklist //FI "PID eq <PID>" 2>/dev/null
powershell.exe -Command "Get-Process -Id <PID> -ErrorAction SilentlyContinue"

# 2. Global lock'u temizle (üzerine yazarak, rm "Device busy" verebilir)
echo "{}" > ~/AppData/Local/hermes/gateway.lock

# 3. Profil lock'larını temizle
echo "{}" > ~/AppData/Local/hermes/profiles/<profil>/gateway.lock
echo "{}" > ~/AppData/Local/hermes/profiles/<profil>/gateway_state.json
```

### 3. Gateway "No Messaging Platforms Enabled" Hatası

Gateway başlar ama Telegram'a bağlanmazsa:

1. **Önce .env'yi doğrula** — token gerçek mi, placeholder `***` değil mi?
2. **Token'ı API'den test et:**
   ```bash
   curl -s "https://api.telegram.org/bot<TOKEN>/getMe"
   ```
   `{"ok":true,"result":{"username":"Kiral38bot",...}}` → token geçerli
   `{"ok":false,"error_code":401,"description":"Unauthorized"}` → **token geçersiz**
3. **`hermes gateway status --profile <profil>` ile snapshot al** — PID, scheduled task, tüm profil durumlarını tek komutta gösterir
4. Gateway log kontrol:
   ```bash
   tail -30 ~/AppData/Local/hermes/profiles/<profil>/logs/gateway.log | grep -E "telegram|connected|platform|token|messaging|error"
   ```
5. Global lock'u kontrol et (önceki gateway hala lock tutuyor olabilir)

### 3b. MCP Server Crash Nedeniyle "No Messaging Platforms Enabled"

Gateway başlar, Telegram'a bağlanmaya çalışmaz (`Connecting to telegram...` satırı log'da yok), direkt `"No messaging platforms enabled."` çıkışı verir.

**Sebep:** MCP server'lardan biri (`powerbi-modeling-mcp`) stdout'a JSON olmayan başlangıç mesajları yazıyor:
```
Detected platform: win32, architecture: x64
Using @microsoft/powerbi... version: 0.5.0-beta.10
```

Bu mesajlar JSON-RPC ayrıştırıcısını çökertir:
```
ERROR mcp.client.stdio: Failed to parse JSONRPC message from server
Invalid JSON: expected value at line 1 column 1
```

MCP client çökünce tüm platform adaptörleri iptal olur → "No messaging platforms enabled."

**Çözüm:** MCP server'ı profile'ın `config.yaml`'ından kaldır:
```yaml
# Silinecek blok:
mcp_servers:
  powerbi:
    command: powerbi-modeling-mcp
    args: ["--start"]
```

**Tespit:** Gateway log'unda `Failed to parse JSONRPC message` varsa ve profil gateway'i çalışıyor ama Telegram bağlanmıyorsa → MCP server stdout kirliliği şüphelen.

### 4. Özet: Multi-Profil Gateway Akışı

```
Kullanıcı "bot çalışmıyor"
  → Hangi bot? 
    → @ReYMeN_ReYMeNbot → profiles/reymen/
    → @Kiral38bot → profiles/kiral38/
    → @Pasa_38_bot → profiles/default/
  → gateway_state.json oku (PID, state, updated_at)
  → PID canlı mı? (ps -p + tasklist fallback)
  → updated_at güncel mi? (>1 saat → zombie)
  → Log'da inbound message var mı?
  → .env'de token gerçek mi?
  → Global lock temiz mi?
  → Gateway restart

Kritik kurallar:
  • Gateway_state.json'daki "running" + "connected"a güvenme
  • PID'yi BİZZAT kontrol et
  • .env'yi ASLA echo/sed ile düzeltme — Python binary kullan
  • Global lock tüm profilleri etkiler — sadece 1 gateway çalışır
```
