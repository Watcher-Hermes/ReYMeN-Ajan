# MIGRATION.md — Geçiş Kılavuzu

> ReYMeN projesinde yapısal değişikliklerin takibi

---

## motor.py Refactor (Planlanan)

### Mevcut Durum
- **Dosya:** `reymen/cereyan/motor.py` — **2,048 satır**, 32 fonksiyon, 1 class (Motor)
- **Kriter:** "2000+ satır → ACİL, hemen böl"

### Hedef Yapı

```
reymen/cereyan/motor/
├── __init__.py           ← Motor class (public API, ~200 satır)
├── arac_registry.py      ← Araç kayıt/listeleme/keşif (~400 satır)
├── arac_calistirici.py   ← Araç çalıştırma/fallback/paralel (~400 satır)
├── provider.py           ← Provider yönetimi/test (~300 satır)
├── cache.py              ← Cache kontrol/kaydet (~150 satır)
└── utils.py              ← Yardımcılar (~150 satır)
```

### Geçiş Takvimi

| Aşama | İçerik | Süre |
|-------|--------|:----:|
| 1 | utils.py + cache.py ayır (bağımsız, önce çıkar) | ~30dk |
| 2 | provider.py ayır (sadece config'e bağımlı) | ~30dk |
| 3 | arac_registry.py ayır (utils + provider'a bağımlı) | ~45dk |
| 4 | arac_calistirici.py ayır (registry'e bağımlı) | ~45dk |
| 5 | __init__.py düzenle (sadece import'lar + public API) | ~30dk |
| 6 | Test + doğrulama | ~30dk |

### Eski → Yeni Import Rehberi

| Eski | Yeni |
|------|------|
| `from reymen.cereyan.motor import Motor` | `from reymen.cereyan.motor import Motor` (aynı) |
| `motor._plugin_araclari_yukle()` | `from reymen.cereyan.motor.arac_registry import plugin_yukle` |
| `motor._cache_kontrol(p)` | `from reymen.cereyan.motor.cache import cache_kontrol` |
| `motor.aktif_provider_listele()` | `from reymen.cereyan.motor.provider import aktif_provider_listele` |

### Breaking Changes
**YOK** — Motor class public API'si korunacak. İç fonksiyonlar _prefix ile ayrı modüllere taşınacak.

---

## Eski Refactor'ler (Tamamlanan)

### Skill Migration (26 June)
| Eski | Yeni | Durum |
|------|------|:-----:|
| `~/AppData/.../reymen/skills/` (78 dosya) | `~/AppData/.../reymen/skills/` (8,822 dosya) | ✅ |
| `reymen/cereyan/skills/Skiller/` (dağınık) | `reymen/cereyan/skills/Skiller/` (37 kategori) | ✅ |

### Hardcoded Path (26 June)
| Eski | Yeni | Durum |
|------|------|:-----:|
| `C:\Users\marko\Desktop\Reymen Proje\hermes_projesi` | `PROJECT_ROOT` env var | ✅ 17 dosya |
| Mutlak yol | `os.path.dirname(__file__)` | ✅ 5 dosya |

---

## Deprecation

| Dosya | Silineceği Tarih | Sebep |
|-------|:----------------:|-------|
| `reymen/cereyan/skills_yeni/` | TBD | Skiller/'a taşındı |
| `cereyan/skills/Skiller/` (eski kök) | TBD | Silinebilir, yedek |
