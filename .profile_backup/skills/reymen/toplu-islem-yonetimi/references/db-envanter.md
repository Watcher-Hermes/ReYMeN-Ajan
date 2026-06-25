# ReYMeN DB Envanteri (10 DB, 22.656 kayıt)

Son güncelleme: 2026-06-21. Tümü 5N1K ile sınıflandırıldı.

## Proje DB'leri

| # | DB | Boyut | Kayıt | Tablo(lar) | 5N1K |
|:-:|:---|:-----:|:-----:|:-----------|:----:|
| 1 | `ogrenmeler.db` | 56KB | 1773 | ogrenmeler | ✅ ne,nerede,nasil,neden,kim |
| 2 | `hafiza.db` | 2MB | 2462 | kayitlar (FTS5), sessions | ✅ |
| 3 | `skills_index.db` (birincil) | 18MB | 7983 | beceriler (FTS5) + beceriler_5n1k | ✅ |
| 4 | `skills_index.db` (ikincil) | 15MB | 7983 | beceriler (FTS5) — birincille senkron | ✅ |
| 5 | `skill_index.db` | 2.2MB | 5781 | skill_fts (FTS5) + skill_5n1k | ✅ (FIX#1+FIX#5) |
| 6 | `ogrenme.db` | 100KB | 228 | ogrenmeler | ✅ (FIX#3) |
| 7 | `session.db` | 464KB | 626 (83 FTS5) | ajan_gunlugu + ajan_gunlugu_5n1k | ✅ (FIX#4) |
| 8 | `hatalar.db` | 16KB | 6 | hatalar | ✅ (FIX#6) |
| 9 | `memory_fts.db` | 28KB | 8 (1 FTS5) | hafiza + hafiza_5n1k | ✅ (FIX#6) |

## Profile DB

| # | DB | Konum | Boyut | Kayıt | 5N1K |
|:-:|:---|:------|:-----:|:-----:|:----:|
| 10 | `state.db` | `~/AppData/Local/hermes/profiles/reymen/` | 10.5MB | 3354 (277 mesaj, 1 session) | ✅ (FIX#4) |

## Boş/Kullanılmayan DB'ler

| DB | Konum | Not |
|:---|:------|:----|
| `kanban.db` | `.ReYMeN/` | 0 kayıt, boş |
| `steering.db` | `reymen/cereyan/.reymen_hafiza/` | 0 kayıt, boş |
| `reymen/arac/.ReYMeN/kanban.db` | Diger kopya | 0 kayıt |
| `.reymen_hafiza/hafiza.db` | Kok dizin | Eski kopya (4656 kayit, dokunulmadi) |

## Yedek DB'ler

`hermes-memory-backup/.ReYMeN/` altında aynı DB'lerin yedek kopyaları var.

## Özet

```
Toplam:   22.656 kayıt
Aktif DB: 10 adet
Tümü 5N1K: ✅
FIX sayısı: 6
```
