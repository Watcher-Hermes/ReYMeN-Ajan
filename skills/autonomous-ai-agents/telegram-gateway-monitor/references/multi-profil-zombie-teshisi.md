---
skill_id: multi-profil-gateway-zombie
usage_count: 1
last_used: 2026-06-23
---

## Multi-Profil Gateway Zombie Teşhisi

> **Olay:** @Kiral38bot çalışmıyor — gateway "running" diyor ama process ölmüş.
> **Tarih:** 23 Haziran 2026 — 3 profilli sistemde doğrulandı.

### Senaryo

Kullanıcı "Bot çalışmıyor" dediğinde **önce hangi bot olduğunu belirle**:
- @ReYMeN_ReYMeNbot → `profiles/reymen/`
- @Kiral38bot → `profiles/kiral38/`
- @Pasa_38_bot → `profiles/default/`

### Zombie Gateway Teşhis Akışı

```
1. Hangi bot? → İlgili profili belirle
2. Profil var mı? → ls ~/AppData/Local/hermes/profiles/<profil>/
3. HIZLI TEŞHİS: hermes gateway status --profile <profil>
   - PID, scheduled task durumu, son çalışma zamanı
   - Tüm profiller: hermes gateway status (parametresiz)
4. gateway_state.json oku → state = "running" veya "stopped"
5. PID var mı? → PID'yi al, BİZZAT doğrula:
   - ps -p <PID> 2>&1 (git-bash — false negative verebilir!)
   - tasklist //FI "PID eq <PID>" (Windows — daha güvenilir)
   - powershell "Get-Process -Id <PID>"
6. updated_at kontrol et → son güncelleme ne zaman?
   - <1dk → canlı
   - 1-30dk → muhtemelen canlı
   - >1 saat → ZOMBIE (özellikle "running" diyorsa)
7. Log kontrol → profile/logs/ içindeki son gateway log'ları
   - "inbound message" en son ne zaman?
   - Hata var mı?
8. .env kontrol → token var mı? API key'ler gerçek mi? (placeholder *** uyarısı)
9. Karar: Zombie mi? → PID ölmüş + state "running" + stale updated_at
```

### Gateway Zaten Çalışıyor Hatası

Gateway'i başlatmaya çalışırken şu hatayı alırsan:

```
✗ Another gateway instance is already running (PID X).
  Use 'hermes gateway restart' to replace it,
  or 'hermes gateway stop' first.
  Or use 'hermes gateway run --replace' to auto-replace.
```

Bu **bir zombie değildir** — gateway sağlıklı çalışıyordur. Çözümler:

| Durum | Yapılacak |
|:------|:----------|
| **Mevcut gateway çalışsın istiyorsan** | `hermes gateway status --profile <profil>` ile doğrula, **hiçbir şey yapma** |
| **Gateway'i yeniden başlatmak istiyorsan** | `hermes gateway run --profile <profil> --replace` |
| **Gateway'i durdurmak istiyorsan** | `hermes gateway stop --profile <profil>` |

**Önemli:** Yeni gateway başlatma denemelerin (`hermes gateway run`) hepsi aynı hatayı verecek — panik yapma, bu beklenen davranış. Background process'ler exit code 1 ile dönecek, sorun yok.

### Background Process Exit Code 127

`hermes gateway run` background process'i **exit code 127** ile biterse:

→ **Komut bulunamadı.** Background shell'inde `hermes` PATH'te değil.
- Çözüm: Tam Python yolu kullan: `python -m hermes_cli.main gateway run --profile <profil>`
- Veya `hermes gateway status` ile gateway'in zaten çalıştığını doğrula

### Bu Oturumda Tespit Edilen (Kiral38 - 23 Haziran 2026)

| Kontrol | Bulgu |
|:--------|:------|
| Profil dizini | ✅ `profiles/kiral38/` var |
| Config | ✅ DeepSeek V4 Flash, aynı ayarlar |
| Bot token | ✅ `.env` içinde, geçerli |
| **gateway_state.json** | ⚠️ `"gateway_state": "running"`, `"platforms.telegram.state": "connected"` |
| **PID (139328)** | ❌ `ps -p` → `PID_NOT_FOUND`, `tasklist` → yok → **process ölmüş** |
| **updated_at** | ❌ `2026-06-23T10:10:23` → **6+ saat önce** |
| **Loglar** | ❌ Sadece PowerBI MCP tools/list — **Telegram aktivitesi 0** |
| Karar | **ZOMBIE** — state "running" ama process yok |

### Zombie vs Diğer Arıza Modları

| Durum | gateway_state | PID | updated_at | Log |
|:------|:-------------|:---:|:-----------|:----|
| **Sağlıklı** | running ✅ | canlı ✅ | <1dk ⚡ | inbound mesaj var ✅ |
| **Zombie** | running ⚠️ | ölmüş ❌ | saatler önce ⏰ | sadece MCP/arkaplan |
| **Polling dondu** | running ✅ | canlı ✅ | güncel ✅ | inbound yok ❌ |
| **Kapalı** | stopped/stopping ✅ | yok ❌ | güncel | — |

### Çözüm

```powershell
# 1. Stale PID/lock dosyalarını temizle (varsa)
rm ~/AppData/Local/hermes/profiles/<profil>/gateway.pid
rm ~/AppData/Local/hermes/profiles/<profil>/gateway.lock

# 2. Gateway state'i sıfırla
powershell.exe -NoProfile -Command "Stop-ScheduledTask -TaskName HermesGateway_<profil> -ErrorAction SilentlyContinue; Start-Sleep 2; Start-ScheduledTask -TaskName HermesGateway_<profil>"

# 3. Doğrula
sleep 15
cat ~/AppData/Local/hermes/profiles/<profil>/gateway_state.json
# Beklenen: "gateway_state": "running", "telegram.state": "connected", updated_at güncel
```

### En Önemli Kural

**gateway_state.json'daki "running" + "connected"a güvenme.** PID'yi BİZZAT kontrol et (`tasklist` ile), `updated_at` zaman damgasına bak. En güvenilir canlılık göstergesi: log'da son `inbound message` zamanı.
