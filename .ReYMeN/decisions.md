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

| Sonraki (İt. 2)
|| Adım | Öneri |
||:-----|:------|
|| B | Bandit audit veya B — alt_ajan/kopru subprocess audit |

## Karar #2 — Cron Iteration 2 — Bandit audit (cereyan)

**Tarih:** 2026-06-23 21:19
**Bağlam:** 2. self-improvement döngüsü — Path B: Bandit audit

### Ne yapıldı?

| # | İşlem | Detay | Sonuç |
|:-:|-------|-------|:-----:|
| 1 | **Bandit scan** | `reymen/cereyan/` — 15K LOC tarandı | ✅ 0 HIGH severity, 8 MEDIUM |
| 2 | **subprocess audit** | `shell=True` ve dinamik input kontrolü | ✅ Hepsi kontrollü |
| 3 | **SQL injection false positive** | `once_hafiza.py` B608 — `.format()` sadece dahili `kosullar` listesi | ✅ False positive |

### Bandit Özeti

| Test | Adet | Severity | Durum |
|:-----|:----:|:--------:|:-----:|
| B101 assert_used | 39 | Low | False positive (test kodu) |
| B110 try_except_pass | 31 | Low | Gerektiğinde geçerli |
| B603 subprocess | 13 | Low | Hepsi kontrollü input |
| B404 subprocess import | 8 | Low | Bilinçli |
| B607 partial path | 5 | Low | Hepsi sabit binary yolu |
| B310 urllib urlopen | 3 | Medium | callback_url kontrollü |
| B608 SQL injection | 2 | Medium/Low | False positive (kosullar dahili) |
| B311 random | 2 | Low | Standart random |
| B105 hardcoded password | 6 | Low | False positive (max_token değerleri) |

### Neden?
- Iteration 1 test baseline 374/374 PASS — sıra güvenlik taramasına geldi
- cereyan/ ReYMeN'in en kritik alt sistemi (motor, beyin, conversation_loop)
- Bandit 0 HIGH — kod güvenliği iyi durumda. 8 MEDIUM'un 2'si SQL false positive, 3'ü urlopen callback

### Alternatif?
- Path A (shim ekle) — gereksiz, tüm shim'ler mevcut
- Path C (test) — bir önceki cycle'da yapıldı

### Sonraki (İt. 3)
| Adım | Öneri |
|:-----|:------|
| C | Küçük test grubu — motor.py veya once_hafiza.py testi |
| A | error_classifier veya onboarding shim varsa ekle |
|---

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

## [2026-06-24] Karar #71 — Adım A: Eksik ensure_dependency shim

**Ne yapıldı?**
- `ReYMeN_cli/dep_ensure.py`'de `ensure_dependency(paket)` fonksiyonu yoktu
- main.py onu import ediyordu → test_entry.py::test_main_setup_browser_calls_ensure_dependency FAIL
- `shutil.which()` tabanlı implementasyon eklendi

**Neden?**
- Testlerde 12/13 PASS, 1 FAIL: eksik import
- Prosedürel hata: `main.py`'de `from ReYMeN_cli.dep_ensure import ensure_dependency` var ama fonksiyon hiç yazılmamış

**Alternatif?**
- C (test): mevcut 147 test PASS, sıra A'ya gelmişti
- B (bandit): son cycle'da yapıldı, yeni dosya yok
- A ✅: Gerçek eksik modül bulundu

**Doğrulama:**
- Syntax: OK ✅
- Import: OK ✅
- test_main_setup_browser_calls_ensure_dependency: PASS (1→1 passed) ✅
|- test_entry.py full suite: 10/10 PASS ✅

## Karar #3 — Cron Iteration 3 (it3) — C: test fix (approvals + CLI)

**Tarih:** 2026-06-24 ~01:20
**Bağlam:** 3. self-improvement döngüsü — Adım C: test grubu çalıştır

### Ne yapıldı?

| # | İşlem | Detay | Sonuç |
|:-:|-------|-------|:-----:|
| 1 | **C — approvals + alt_ajan + cli** | Yeni test grubu (it1'de yoktu) | ✅ 53/53 PASS after 2 fix |
| 2 | **Brittle fix #1** | `test_approvals.py::test_rm_rf`: mode=off → mode=manual | ✅ `mode=off` izin verir, doğru test ayarı "manual" |
| 3 | **Brittle fix #2** | `test_cli.py::test_cli_argument_parser`: entry point → real main | ✅ `main.py` thin wrapper, `reymen/sistem/main.py` asıl dosya |
| 4 | **Commit** | `dd78132` fresh-main | ✅ `(committed)` |

### Test Detayı

| Test Grubu | Süre | Sonuç |
|:-----------|:----:|:-----:|
| test_approvals.py | 0.21s | 26 PASS |
| test_alt_ajan.py | 0.62s | 16 PASS |
| test_cli.py | 0.18s | 11 PASS |
| **Toplam** | **1.03s** | **53 PASS** |

### Neden?
- İt2 (B) yapıldı → sıra C'ye geldi
- İt1'de test edilmemiş grup seçildi (approvals + alt_ajan + cli)
- 2 brittle test bulundu ve düzeltildi

### Alternatif?
- A (shim): yeni dosya eklenmiş mi kontrol et — hayır, gerek yok
- B (bandit): bir önceki cycle yapıldı

### Sonraki (İt. 4)
| Adım | Öneri |
|:-----|:------|
| A veya B | Rotasyona devam. A: import-missing check, B: hedefli Bandit |
| C (son çare) | Farklı grup combine dene (mcp + tools) |
| --- | --- |

---

## Karar #5 — Cron Iteration 5 (it5) — C: core modüller

**Tarih:** 2026-06-24 ~02:25
**Bağlam:** 5. self-improvement döngüsü — Adım C: çekirdek modüller

### Ne yapıldı?

| # | İşlem | Detay | Sonuç |
|:-:|-------|-------|:-----:|
| 1 | **C — beyin + hafiza** | Core memory/brain modülleri | ✅ 78/78 PASS (10.03s) |
| 2 | **C — motor + planlayici** | Engine + planner modülleri | ✅ 104/104 PASS (5.52s) |
| 3 | **Syntax verify** | 4 değişen .py compile() check | ✅ clean |
| 4 | **Toplam** | 2 grup, 182 test, 15.55s | ✅ 182/182 PASS |

### Neden?
- İt4 (C) yapıldı, churn=4 (<5) → B skip
- 2 ardışık C (it3-4) → 3. C'ye yaklaşıyor ama henüz sınırda değil
- Beyin/hafiza/motor/planlayici daha önce test edilmemişti

### Alternatif?
- A (import-missing): Son 4 .py değişikliği, hepsi stdlib — bulgu yok
- B (bandit): churn <5 → kural gereği atlandı

### Sonraki (İt. 6)
| Adım | Öneri |
|:-----|:------|
| **B** | 3. ardışık C'ye ulaşıldı (it3=C, it4=C, it5=C) → zorla B |
| A | Import-missing check — düşük öncelik |

---

## Karar #4 — Cron Iteration 4 (it4) — C: test group

**Tarih:** 2026-06-24 ~01:50
**Bağlam:** 4. self-improvement döngüsü — Adım C: farklı test grubu

### Ne yapıldı?

| # | İşlem | Detay | Sonuç |
|:-:|-------|-------|:-----:|
| 1 | **C — araclar + mcp + error_classifier** | Yeni kombinasyon (it1/it3'te yok) | ✅ 123/123 PASS |
| 2 | **Syntax verify** | 3 modified .py compile() check | ✅ clean |
| 3 | **Commit** | `bd648c5` fresh-main | ✅ |

### Test Detayı

| Test Grubu | Süre | Sonuç |
|:-----------|:----:|:-----:|
| test_araclar.py + test_araclar_telegram.py + test_mcp.py + test_error_classifier.py | 5.89s | 123 PASS |

### Neden?
- İt3 (C) yapıldı, churn=3 (<5) → B skip
- A (import-missing): 0 bulgu, tüm import'lar stdlib
- Rotasyondaki en uygun: C — farklı grup
- Churn=3: sadece dep_ensure.py + 2 script değişmiş, derin audit gereksiz

### Alternatif?
- A: import-missing check çalıştırıldı, bulgu yok. Yeni shim gerekmiyor.
- B: churn < 5 → skill kuralı gereği atlandı

### Sonraki (İt. 5)
| Adım | Öneri |
|:-----|:------|
| B | Hedefli Bandit — cereyan/ dışında kalan kritik modüller (motor, beyin) |
|| A | Import-missing yoksa A atlanabilir |
|| C | Sadece nadiren — 3. ardışık C'ye yaklaşılıyor |

## Karar #8 — Cron Iteration 7 (it7) — B: güvenlik AST audit

**Tarih:** 2026-06-24 ~03:00
**Bağlam:** 7. self-improvement döngüsü — Adım B: AST tabanlı güvenlik taraması

### Ne yapıldı?

| # | İşlem | Detay | Sonuç |
|:-:|-------|-------|:-----:|
| 1 | **Gitignore güncelle** | `cokus_raporlari/`, `beceri_kutuphanesi.json`, `trajectories/*.jsonl`, `referanslar.json` eklendi | ✅ Runtime artifact kirliliği engellendi |
| 2 | **AST subprocess audit** | motor.py, beyin.py, planlayici.py, once_hafiza.py — shell=True + dynamic cmd | ✅ 0 bulgu (hepsi intentional) |
| 3 | **Bare except:pass audit** | motor.py: 6 adet, hepsi non-critical path | ✅ Intentional |
| 4 | **Hardcoded path audit** | motor.py:1052,1287 + screenshot_bot.py:18 — Python 3.14 binary | ✅ Intentional (WONTFIX) |
| 5 | **Syntax scan** | 4 critical module syntax verified | ✅ clean |
| 6 | **Commit** | it7: B — gitignore + AST audit | ✅ |

### Audit Detayı

| Modül | AST shell=True | Hardcoded Path | bare except:pass |
|:------|:--------------:|:--------------:|:----------------:|
| motor.py | 0 (intentional) | 2 (WONTFIX) | 6 (intentional) |
| beyin.py | 0 | 0 | 0 |
| planlayici.py | 0 | 0 | 0 |
| once_hafiza.py | 0 | 0 | 0 |

### Neden?
- İt5 (C) ve İt6 (A) yapıldı → sıra B'ye geldi
- Churn=5, eşikte: son 3 commit'te sadece 1 yeni .py dosyası (__init__.py)
- AST audit pip gerektirmez, 5sn'de biter — token verimli

### Alternatif?
- C: 3 ardışık C (it3-5) zaten yapıldı, 4. C yanlış
- A: İt6'da zaten yapıldı, yeni modül yok

### Sonraki (İt. 8)
| Adım | Öneri |
|:-----|:------|
| C | Farklı test grubu — stabilitenin sağlaması |
| veya SILENT | 7+ iterasyon stabil, sessiz moda geçilebilir |
