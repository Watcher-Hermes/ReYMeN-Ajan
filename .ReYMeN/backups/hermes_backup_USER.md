Turkish-speaking user (native Turkish, opens in Turkish). Detail-oriented, quality-focused.
§
Runs structured QA/evaluation pipelines against other AI agents (ReYMeN). Workflow: batch questioning -> error analysis -> correction -> feedback. Values precise, unambiguous answers with code examples.
§
ReYMeN testing — option C: ReYMeN'e test olduğu söylenmez, doğal hali test edilir. Batch sonrası hatalar bildirilerek öğrenme döngüsü sağlanır. A+B kombinasyonu da teklif edildi ama C seçildi.
§
Approval preference: "Allow once seçili tüm onayların otomatik seç ilerle sorma" — wants all command approvals auto-accepted without prompt. Enable auto-approve mode when working.
§
ReYMeN alt_ajan.py test workflovu: (1) Mock test (test_alt_ajan_mock.py) — threading/lock/sonuç toplama izole test (2) Gerçek WEB_ARA testi (3) İzinli araç seti. 5 test senaryosu: temel akış, 5 eşzamanlı görev, hata yakalama, max_adim sınırı, state kontrolü. Skill: alt-ajan-mock-test.
§
ZORUNLU KURAL — Skill yükleme/güncelleme çift yönlü: "yükle" veya "skill yükle" dendiğinde HER ZAMAN (1) ReYMeN local skill kütüphanesine yükle/güncelle, (2) GitHub Watcher-Hermes/hermes-skills reposuna push et, (3) gerekiyorsa README.md güncelle. İkisi değil, üçü de yapılır. Kullanıcı "hermes-skills reposuna atmadın mı" diyerek bu beklentiyi netleştirdi.
§
Teknik olarak kesin ve doğrulanmış bilgi bekler. "Çalışmaz" veya "sadece GUI'den yapılır" gibi yüzeyel cevapları kabul etmez — neden çalışmadığını, hangi parametrenin ne olduğunu, alternatif doğru yolun ne olduğunu görmek ister. Her iddianın log/test ile kanıtlanmasını bekler. Yanlış bilgi skill'de görürse hemen düzeltilmesini ister, eski hatalı referansların temizlenmesini talep eder.
§
Work stili: planla/onaysız uygula. Ağır kod = Claude Code'a devret. ÖNCE/SONRA metrik, tablo, puan ister. Batch paralel çalışma, sık rapor. Seçenek sorulursa Allow once seçilip onay beklenmeden ilerlenir. Tam mimari şeffaflık ister — tüm dizinler kontrol edilmeden rapor verilmez.
§
User confirmed again (14 June 2026): "Kalıcı olarak söylüyorum artık seçenek sorar isen Allow once seçerek ilerle onay bekleme" — the Allow Once auto-select rule is permanent and applies to ALL choice prompts (screen dialogs AND in-chat questions). Never ask the user for approval — silence = continue.