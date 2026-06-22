# Proje OneDrive Dışına Taşıma
> 20 Haziran 2026

## Sorun
OneDrive Desktop senkronizasyonu proje dosyalarını buluta yüklüyordu. Büyük önbellek dosyaları (node_modules, venv, skill_backup) senkronizasyon sorunlarına yol açıyordu.

## Yapılan İşlem

**Kaynak:** `C:\Users\marko\OneDrive\Desktop\Reymen Proje\hermes_projesi`
**Hedef:** `C:\Users\marko\Desktop\Reymen Proje\hermes_projesi`

**Robocopy ile kopyalandı** (venv, node_modules, .git hariç - /E /XD ile exclude):
- 275+ .py dosyası
- Tüm alt dizinler (testler, ReYMeN CLI, telegram_bot, vs.)
- `.vscode/settings.json` eklendi (Pyright TOML sorunu çözümü)

**Hariç tutulanlar (mevcut değilse kopyalanmadı):**
- `venv/`, `bot_venv/`, `node_modules/`, `.git/`, `__pycache__/`, `.pytest_cache/`, `.cron_logs/`, `logs/`, `skills_backup/`, `skills_backup_*`

**OneDrive'daki orijinal kopya** — olduğu gibi bırakıldı, silinmedi, değiştirilmedi.

## Yedekleme Klasörleri (Junction ile C:\ sürücüsüne taşındı)

| Klasör | Hedef | Boyut |
|--------|-------|-------|
| `hermes-backup` | `C:\hermes-backup` | ~445 MB |
| `ReYMeN-full-backup` | `C:\ReYMeN-full-backup` | ~500 MB |
| `hermes-memory-backup` | `C:\hermes-memory-backup` | ~0.1 MB |
| `hermes-skills-backup` | `C:\hermes-skills-backup` | ~38 MB |

**Silinen geçici dosyalar:** `.pytest_cache`, `ReYMeN-full-backup-tmp`, `__pycache__`

## VPN / Network

- **VPN (CyberGhost)**: Açılması gerekiyor mu? Bilinmiyor — bazı durumlarda bağlantı sorunu yaşandı.
