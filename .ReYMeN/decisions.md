
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
