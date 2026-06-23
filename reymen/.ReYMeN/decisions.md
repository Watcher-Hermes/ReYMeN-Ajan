
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
