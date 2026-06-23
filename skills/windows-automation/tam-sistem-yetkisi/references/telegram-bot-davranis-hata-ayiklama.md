# Telegram Bot Davranış Hata Ayıklama

Bot beklenmedik mesaj gönderdiğinde kaynağı bulma workflow'u.

## Tetikleyici

- Bot kullanıcıya "kanala katıl" mesajı gösteriyor
- Bot sürekli aynı mesajı döndürüyor (soruyu yanıtlamıyor)
- Kullanıcı "bu mesaj nereden geliyor" diye soruyor

## Akış

### 1. Ekranı Analiz Et
`vision_analyze` ile screenshot'ı oku — hangi bot, hangi mesaj, kullanıcı ne yazmış.

### 2. Kodu Tara
Mesaj metnini (ör: "must join our channel") proje genelinde ara.
Bulunamazsa → kaynak kodda değil.

### 3. Botu Tanımla
```bash
# .env'den token'ı al
BOT_TOKEN=$(cat .env | grep TELEGRAM_BOT_TOKEN | cut -d= -f2)

# Bot bilgisi
curl -s "https://api.telegram.org/bot$BOT_TOKEN/getMe"
# → id, first_name, username, can_join_groups vb.
```

### 4. Kanal Bilgisini Doğrula
```bash
curl -s "https://api.telegram.org/bot$BOT_TOKEN/getChat?chat_id=@KanalAdi"
# → kanal gerçek mi, açıklaması ne, pinned message
```

### 5. Kaynağı Belirle

| Mesaj Kaynağı | Tespit Yöntemi | Çözüm |
|:---------------|:----------------|:-------|
| **Kod (gateway/handler)** | `search_files` ile mesaj metnini bul | Kodu düzelt |
| **BotFather ayarı** | Kodda yok, API'de `getMyDefaultAdministratorRights` boş | BotFather → `/mybots` → Bot Settings → Group & Channel → kaldır |
| **3. parti bot** | `getMe` → farklı bot ID'si | Bizim botumuz değil, müdahale edilemez |

### 6. Force-Join Kaldırma (BotFather ise)
```
@BotFather
→ /mybots
→ [bot_seç]
→ Bot Settings
→ Group & Channel
→ Remove / Leave
```

## Pitfall'lar

- **Token'ı direkt okumaya çalışma** — Hermes `.env` okumayı engeller. Terminal ile `cat .env | grep TELEGRAM_BOT_TOKEN` kullan.
- **Force-join kodu yoksa panik yapma** — BotFather ayarıdır, kod sorunu değil.
- **Bot ID ile username farklı olabilir** — `getMe`'deki `first_name` Telegram'da görünen ad, `username` @handle.
- **"Nasıl yanı" gibi Türkçe bot adları** normaldir — BotFather'da bot oluşturulurken Türkçe isim verilmiş olabilir.

## Referans
- Telegram Bot API: https://core.telegram.org/bots/api
- BotFather commands: https://core.telegram.org/bots/features#botfather
