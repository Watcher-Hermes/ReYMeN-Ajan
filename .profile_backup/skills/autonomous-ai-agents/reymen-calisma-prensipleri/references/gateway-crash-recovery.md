# Gateway Crash Recovery — Session Referansı

## Kaynak: 23 Haziran 2026 — Kiral38 + Pasa_55 kurtarma

### Olay Kronolojisi

| Zaman | Olay |
|:------|:------|
| 13:08 | Kiral38 token InvalidToken hatası — Telegram reddetti |
| 13:10 | Yeniden başlatma → çalıştı |
| 17:00 | Gateway restart → "No messaging platforms enabled" (PowerBI MCP) |
| 17:25 | PowerBI MCP kaldırıldı, gateway çalıştı |
| 17:25+ | Tüm botlar aktif |

### Alınan Dersler

1. **Token revoked** → BotFather'dan yeni token al, .env'ye yaz
2. **PowerBI MCP çökertiyor** → stdout non-JSON satırlar basar
3. **Stale lock** → `echo "{}" > gateway.lock` ile üzerine yaz, silinemezse
4. **Global lock** → aynı yöntem `~/AppData/Local/hermes/gateway.lock`
5. **Runtime lock conflict** → "Another gateway instance is already running" NORMAL, mevcut PID kullanılır
6. **.env bozulursa** → çalışan profilden kopyala + token değiştir (Python ile)
