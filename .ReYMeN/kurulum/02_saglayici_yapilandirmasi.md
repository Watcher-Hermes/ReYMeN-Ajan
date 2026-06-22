# Sağlayıcı (Provider) Yapılandırması
> Kaynak: 19-20 Haziran 2026 oturumları

## Aktif Sağlayıcı: DeepSeek (deepseek-v4-flash)

DeepSeek API key: `sk-43426169...88c4` (`.env`'de)
Ana profil: reymen → `config.yaml`'de `provider: deepseek`

## Yedek Sağlayıcı: OpenRouter

OpenRouter API key: `sk-or-v1-...058a`
DeepSeek 402 (Insufficient Balance) hatası alırsa OpenRouter fallback.

## Bilinen Sorunlar

1. **DeepSeek 402 Payment Required**: Zaman zaman bakiye yetersiz kalır. OpenRouter devreye girer.
2. **OpenRouter API key yorum satırındaydı**: ReYMeN projesi `.env`'sinden ReYMeN ana `.env`'sine kopyalandı ve aktifleştirildi.
3. **`.env`'de `DEEPSEEK_API_KEY=sk-0370...4f` literal yazılmıştı**: Gerçek key ile değiştirildi.

## API Key'lerin Konumu

```
~/.hermes/.env:
  DEEPSEEK_API_KEY=sk-434...88c4
  OPENROUTER_API_KEY=sk-or-...058a
  TELEGRAM_BOT_TOKEN=89253...rwUM

~/AppData/Local/hermes/profiles/reymen/.env:
  TELEGRAM_BOT_TOKEN=87741...72tU
  DEEPSEEK_API_KEY=sk-434...88c4
  GATEWAY_ALLOW_ALL_USERS=true
```
