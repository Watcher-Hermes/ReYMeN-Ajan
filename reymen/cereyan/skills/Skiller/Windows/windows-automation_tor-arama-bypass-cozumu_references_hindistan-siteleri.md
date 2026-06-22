# Hindistan Siteleri — Tor Erişim Durumu

## Çalışan

### GBHackers
```
GET https://gbhackers.com/?s={urllib.parse.quote('bluetooth sniffing')}
```
- Direkt çalışır ✅
- SSH 200, ~193KB
- Gerçek güvenlik içeriği

### Bing IN
```
GET https://www.bing.com/search?q={urllib.parse.quote('bluetooth sniffing attack security')}&cc=IN
```
- 10 sonuç ✅
- HTTP 200, ~122KB

## Bloklu
- `thehackernews.com` — HTTP 403 Cloudflare ❌
- `securityweek.com` — HTTP 403 ❌

GBHackers en güvenilir Hint güvenlik kaynağıdır.
