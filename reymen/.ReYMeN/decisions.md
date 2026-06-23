
## Karar #26 — once_hafiza Drift Düzeltmesi — 2026-06-23
**Durum:** cereyan/ ve sistem/ once_hafiza.py arasında drift vardı.
  - Aynı işlev için 2 farklı DB (cereyan/.ReYMeN/ogrenmeler.db vs hafiza/ogrenme.db)
  - Sigmoid güven hesaplaması sadece cereyan'da çalışıyordu
  - 4 fonksiyon (_kademeli_guven, belirsiz_gorev_cozumle, _benzerlik_skoru, eski_kayitlari_temizle) sistem'de ya yoktu ya da kopyaydı
**Yapılan:** 
  - 4 fonksiyon cereyan'dan import edildi (kopyalama değil, import — tek kaynak)
  - sistem/once_hafiza.py cereyan/once_hafiza.py'ye delege eder oldu
  - DB birleştirildi: cereyan/.ReYMeN/ogrenmeler.db TEK kaynak
  - duplicate_module_detector.py oluşturuldu (scripts/)
  - Skill oluşturuldu: devops/duplicate-module-detector
  - Env validator düzeltildi: 3 profil base_url boş → https://api.deepseek.com
**Alternatif:** Kopyayı korumak (reddedildi — drift devam ederdi)
**Sonuç:** ✅ Test geçti. Sigmoid CLI'da çalışıyor. Duplicate detector 122 sorun buldu (çoğu test/backup gürültüsü, 6 gerçek benzer modül var)
**Sonraki:** duplicate_module_detector cron'a bağlanacak

## [2026-06-23] KALICI KURAL: Duplicate Modül Drift'i

**Olay:** cereyan/once_hafiza.py (639 satır, 12 fonksiyon) ile
sistem/once_hafiza.py (669 satır, class-based) aynı isimde ama
farklı içerikte iki dosyaydı. main.py (gerçek kullanıcı yolu)
eski/eksik sistem/ versiyonunu import ediyordu. 4 gelişmiş özellik
(sigmoid güven, belirsiz görev çözümleme, benzerlik skoru, eski
kayıt temizleme) hiçbir zaman production'da çalışmadı.

**Kök sebep:** Aynı isim + farklı klasör → "zaten var" sanıldı,
karşılaştırma yapılmadı.

**Kalıcı kural:**
- Her cycle başında `duplicate_module_detector.py` otomatik çalışır.
- Aynı isimli dosya bulunursa, içerik karşılaştırması ZORUNLU.
- Hiçbir zaman iki kopya "geçici çözüm" olarak bırakılmaz —
  ya import/merge edilir ya da biri silinir.
- "Her şey temiz" raporu, bu kontrol çalıştırılmadan verilemez.
