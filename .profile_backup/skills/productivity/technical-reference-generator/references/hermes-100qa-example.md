# Hermes Agent 100 Q&A — Example Output Structure

## Dosya: HERMES_TEKNIK_100_SORU.md

- Boyut: 667 satır, 57.7KB
- İçerik: 100 teknik soru-cevap, 10 bölüm
- Format: SORU → CEVAP → YOL (Akış/Dosya)

## Bölüm Yapısı

| Bölüm | Soru | Konu |
|-------|------|------|
| GENEL MİMARİ | 1-15 | Temel yapı, config, conversation loop |
| HAFIZA SİSTEMİ | 16-30 | 5 katman: MEMORY.md, OnceHafıza, FTS5, decisions.md, state.db |
| SKİLL SİSTEMİ | 31-45 | 1130+ skill, 5N1K, YAML format |
| GATEWAY | 46-55 | gateway_state.json, lock, timeout |
| TOOL SİSTEMİ | 56-65 | 50+ tool, built-in + on-demand |
| CRON | 66-75 | no_agent, deliver modes |
| PROFİL | 76-85 | Multi-profile, shared_memories |
| GÜVENLİK | 86-92 | Yasaklar, approval modları |
| ALT AJAN | 93-98 | Leaf/orchestrator, batch |
| KARAR DÖNGÜSÜ | 99-100 | Adaptif öğrenme |

## Tarama Adımları (Bu çıktı için kullanılan)

1. `ls -la ~/.hermes/profiles/reymen/` — profil dizin yapısı
2. `read_file(config.yaml)` — tüm config alanları
3. `read_file(SOUL.md)` — kimlik ve kurallar
4. `read_file(decisions.md)` — karar geçmişi
5. `find .ReYMeN/ -maxdepth 2 -type d` — 40+ alt klasör
6. `find reymen/ -name "*.py"` — cereyan/arac/hafiza modülleri
7. `find skills/ -maxdepth 2 -type d` — skill dizinleri

## Subagent Prompt Yapısı

```
goal: Write 100 Turkish Q&A pairs about [system]...
context: [all scanned paths, config contents, module lists]
toolsets: ["file", "terminal"]
```

Subagent'a verilen bağlam:
- config.yaml içeriği (tüm alanlar)
- SOUL.md içeriği (kimlik, kurallar)
- .ReYMeN/ dizin listesi (40+ klasör)
- reymen/ modül yapısı (cereyan, arac, hafiza)
- skills/ dizin yapısı
- Memory sistemi detayları
- Gateway/Cron/Profile yapıları
