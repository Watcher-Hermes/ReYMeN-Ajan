
---

## [2026-06-23] Kalıcı Kural: Duplicate Modül Drift'i

**Olay:** `cereyan/once_hafiza.py` (639 satır, 12 fonksiyon) ile
`sistem/once_hafiza.py` (669 satır, class-based) aynı isimde ama
farklı içerikte iki dosyaydı. main.py (gerçek kullanıcı yolu)
eski/eksik sistem/ versiyonunu import ediyordu. 4 gelişmiş özellik
(sigmoid güven, belirsiz görev çözümleme, benzerlik skoru, eski
kayıt temizleme) hiçbir zaman production'da çalışmadı.

**Kök sebep:** Aynı isim + farklı klasör → "zaten var" sanıldı,
karşılaştırma yapılmadı.

**Kalıcı kural:**
- Her cycle başında `scripts/duplicate_module_detector.py` otomatik çalışır.
- Aynı isimli dosya bulunursa, içerik karşılaştırması **ZORUNLU**.
- Hiçbir zaman iki kopya "geçici çözüm" olarak bırakılmaz —
  ya import/merge edilir ya da biri silinir.
- "Her şey temiz" raporu, bu kontrol çalıştırılmadan verilemez.

---

## [2026-06-23] Kalıcı Kural: Duplicate Modül Drift'i

**Olay:** `cereyan/once_hafiza.py` (639 satır, 12 fonksiyon) ile
`sistem/once_hafiza.py` (669 satır, class-based) aynı isimde ama
farklı içerikte iki dosyaydı. main.py (gerçek kullanıcı yolu)
eski/eksik sistem/ versiyonunu import ediyordu. 4 gelişmiş özellik
(sigmoid güven, belirsiz görev çözümleme, benzerlik skoru, eski
kayıt temizleme) hiçbir zaman production'da çalışmadı.

**Kök sebep:** Aynı isim + farklı klasör → "zaten var" sanıldı,
karşılaştırma yapılmadı.

**Kalıcı kural:**
- Her cycle başında `scripts/duplicate_module_detector.py` otomatik çalışır.
- Aynı isimli dosya bulunursa, içerik karşılaştırması **ZORUNLU**.
- Hiçbir zaman iki kopya "geçici çözüm" olarak bırakılmaz —
  ya import/merge edilir ya da biri silinir.
- "Her şey temiz" raporu, bu kontrol çalıştırılmadan verilemez.

---

## Karar #1 — Cron Iteration 1 — Test baseline (fresh-main)

**Tarih:** 2026-06-23 06:29
**Bağlam:** Self-Improvement cron — 15dk döngüsü, fresh-main branch'ine ilk çalışma

### Ne yapıldı?

| # | İşlem | Detay | Sonuç |
|:-:|-------|-------|:-----:|
| 1 | **Syntax scan** | 10,693 .py dosyası ast.parse() ile tarandı | ✅ 10,677 OK, 16 FAIL (hepsi backup/archive) |
| 2 | **C — Test run** | Core test suite: acp+acp_server+achievements+adaptif+agent_core+redact+akil+beyin+motor | ✅ **374 PASS** (0 fail) |
| 3 | **Commit** | fresh-main'e ilk cron commiti | ✅ `(committed)` |

### Test Detayı

| Test Grubu | Süre | Sonuç |
|:-----------|:----:|:-----:|
| test_acp.py + test_acp_server.py | 3.04s | 53 PASS |
| test_achievements.py + test_adaptif_ogrenme.py + test_agent_core.py | 15.58s | 111 PASS |
| test_agent_redact.py + test_agent_redact_new.py + test_agent_think_scrubber.py + test_akil.py + test_beyin.py + test_motor.py | 6.75s | 210 PASS |
| **Toplam** | **25.37s** | **374 PASS** |

### Neden?
- fresh-main branch'ine ilk cron çalışması — test baseline'ı oluşturmak için C adımı seçildi
- Tüm syntax ve core testler temiz çıktı

### Alternatif?
- Bandit taraması yapılabilirdi ama henüz test baseline yoktu
- Shim ekleme de yapılabilirdi — testler zaten passed, gerek kalmadı

### Sonraki (İt. 2)
| Adım | Öneri |
|:-----|:------|
| B | Bandit audit veya B — alt_ajan/kopru subprocess audit |
