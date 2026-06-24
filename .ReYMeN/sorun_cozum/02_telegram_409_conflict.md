# Telegram 409 Conflict Hatası Çözümü
> 20 Haziran 2026

## Sorun
Gateway başlatılırken "Telegram polling conflict" hatası:
```
WARNING gateway.platforms.telegram: [Telegram] Telegram polling conflict (1/5) — 
previous session still held open on Telegram's servers. Waiting 20s for it to expire.
Error: Conflict: terminated by other getUpdates request
```

## Neden
Aynı bot token'ı ile 2 ayrı process Telegram'ı polling yapmaya çalışıyor. Telegram API aynı token için sadece 1 getUpdates session'ına izin verir.

## Çözüm

### 1. Anlık Çözüm (session sıfırlama)
```bash
BOT_TOKEN=...  # .env'den oku
curl -s "https://api.telegram.org/bot${BOT_TOKEN}/getUpdates?offset=-1&timeout=1"
```
Veya 20-30 saniye bekleyin — Telegram eski session'ı otomatik kapatır.

### 2. Kalıcı Çözüm
Her bot token'ı **ayrı profilde** çalıştırın:
```bash
hermes profile create <yeni-profil>
yes Y | hermes -p <yeni-profil> gateway start
```

### 3. Hangi Process Çakışıyor (tespit)
```bash
ps aux | grep python | grep -i telegram
tasklist //FI "IMAGENAME eq python.exe"
```

## Kapsamlı Düzeltme (19 Haziran)
- `.env`'de TELEGRAM_BOT_TOKEN comment içindeydi → aktifleştirildi
- `GATEWAY_ALLOW_ALL_USERS=true` eklendi
- Gateway yeniden başlatıldı
- DeepSeek API key ana `.env`'ye eklendi (reymen profilinden kopyalandı)
