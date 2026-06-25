---
name: closed-learning-loop-5-asama
description: ReYMeN'in 5 aşamalı kapalı öğrenme döngüsü — observe → discover → compare → test → save
created: 2026-06-23
usage_count: 1
last_used: 2026-06-23
---

# closed-learning-loop-5-asama

ReYMeN'in `ClosedLearningLoop` sınıfı üzerinden çalışan 5 aşamalı otonom öğrenme döngüsü.

## 5N1K

| Soru | Cevap |
|------|-------|
| **Kim** | ReYMeN Agent (ClosedLearningLoop sınıfı) |
| **Ne** | 5 aşamalı meta-öğrenme döngüsü — observe → discover → compare → test → save |
| **Nerede** | `reymen/cereyan/closed_learning_loop.py` (1166 satır, 46KB) |
| **Ne Zaman** | `run_forever()`: her 24 saatte bir. Ayrıca 5 tetikleyici noktada |
| **Neden** | Kendi kendini geliştirme, web'den yeni yöntem öğrenme, beceri boşluklarını doldurma |
| **Nasıl** | FTS5 indeksi + DuckDuckGo arama + sandbox test + .md beceri kartı oluşturma |

## Aşamalar

### 1. observe_self()
- Mevcut tüm becerileri FTS5 DB'den al
- Zayıf alan (aciklama <20 karakter) vs güçlü alan tespiti
- Döndürür: `{weak_areas, strong_areas, total_skills, last_run}`

### 2. discover_better_methods(focus)
- DuckDuckGo'da `"best practice {focus} coding tutorial"` ara
- HTML parse → max 5 sonuç
- Fallback: varsayılan yöntem

### 3. compare_and_decide(current, new)
- Skorlama: kaynak URL (+2), ad (+1), uzun özet (+1), farklılık (+1)
- Karar: UYGULA (≥3), DAHA_FAZLA_ARAŞTIR (≥1), REDDET

### 4. test_in_sandbox(method)
- Syntax compile kontrolü
- Skor: ad (+2), kaynak URL (+3), taban (5)

### 5. save_as_skill(method, score)
- `beceri_kristallestir()` çağrısı
- FTS5'te duplicate kontrol → yoksa yeni .md, varsa merge

## Tetikleyiciler (5 nokta)

1. **Görev tamamlanınca** (gorev_hafiza.py:160-173) — `tecrube_kaydet()` başarılı görev sonrası
2. **main.py _ogren()** (main.py:1230-1235) — adım_geçmişi varsa kristalleştir
3. **Dinamik araç üretimi** (dinamik_arac_uretici.py:179-187) — yeni araç test geçerse
4. **Arka plan beceri gözden geçirme** (agent_runtime.py:190-205) — BackgroundReview LLM gözlemi
5. **Cron / CLI** — `--ogren`, `--self-improve`, cron job (30dk/7gün)

## Önemli Metrikler

- FTS5 DB: `skills_index.db`, ~19000 kayıt
- Prompt enjeksiyonu: `beceri_baglamini_al(sorgu, adet=3)` → max 4000 karakter
- Thread-safe: her method kendi SQLite connection açar/kapatır
- WAL modu: okuma-yazma çakışması minimize

## Püf Noktaları

- `auto_index=False` varsayılan (production performansı); startup'ta manuel `tum_becerileri_indeksle()` çağrılmalı
- `_fts5_benzer_beceri_ara()` duplicate kontrolü için önce FTS5'te sorgu atar
- `test_in_sandbox()` sadece syntax kontrolü yapar — gerçek runtime testi için `run_forever()` dışında ek doğrulama gerekebilir
- `compare_and_decide()` skorlama basit kurallı — LLM tabanlı değil
