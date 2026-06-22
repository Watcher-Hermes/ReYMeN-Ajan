# Telegram Profilleri ve Bot Yapılandırması
> Kaynak: 10+ oturum (19-20 Haziran 2026)
> Son güncelleme: 20 Haziran 2026

## Profil Yapısı

| Profil | Bot | Token (masked) | Görev |
|--------|-----|----------------|-------|
| **default** | @Pasa_38_bot | `8925395268:AAF3...rwUM` | ReYMeN (standart) |
| **reymen** | @ReYMeN_ReYMeNbot | `8774151638:AAFN...72tU` | ReYMeN özel ajan |

## Her Profile Ayrı Gateway Çalıştırma

### Kural (KESİN)
Her Telegram bot token'ı **ayrı bir ReYMeN profili** gerektirir. Aynı token'ı 2 process kullanırsa `409 Conflict` hatası alınır.

### Kurulum Adımları

```bash
# 1. Yeni profil oluştur
hermes profile create <profil-adi>

# 2. Profile token'ı yaz
echo "TELEGRAM_BOT_TOKEN=<token>" > ~/AppData/Local/hermes/profiles/<profil-adi>/.env
echo "GATEWAY_ALLOW_ALL_USERS=true" >> ~/AppData/Local/hermes/profiles/<profil-adi>/.env

# 3. Gateway'i kur ve başlat
yes Y | hermes -p <profil-adi> gateway install
yes Y | hermes -p <profil-adi> gateway start

# 4. Durumu kontrol et
hermes -p <profil-adi> gateway status
```

### Bot Token Lokasyonları

- **default**: `~/AppData/Local/hermes/.env`
- **reymen**: `~/AppData/Local/hermes/profiles/reymen/.env`

## Gateway Banner (Dinamik İsim)

Gateway başlangıç banner'ı artık profil adını gösterir:

- `default` profil → `⚕ ReYMeN Gateway Starting...`
- `reymen` profil → `⚕ ReYMeN Gateway Starting...`

Değişiklik: `hermes_cli/gateway.py:4107-4128` — `_profile_suffix()` fonksiyonu ile.

## Bilinen Sorunlar

1. **409 Conflict**: Eski session Telegram sunucusunda hala açıkken yeni gateway başlatılır. Çözüm: getUpdates ile offset sıfırla veya 20sn bekle.
2. **raft CLI warning**: raft CLI PATH'te yok — isteğe bağlı, işlevi etkilemez.
3. **TOML dosyası VS Code'da hatalı görünür**: Pyright .toml'u Python parse eder. `.vscode/settings.json` ile düzeltildi.

## Skill Kaydı

- `multi-telegram-gateway-profiles` — her bot token'ı için ayrı profil + gateway
- `telegram-bot-troubleshooting` — bağlantı sorunları için
