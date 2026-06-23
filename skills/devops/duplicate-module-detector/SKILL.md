---
name: duplicate-module-detector
description: "AST tabanlı drift/duplicate tespit scripti. Aynı isimli dosyaları farklı klasörlerde bulur, fonksiyon setlerini karşılaştırır, drift varsa raporlar. Hangi dosyanın canlı yol olduğunu tespit eder."
version: 1.0.0
category: devops
---

# Duplicate Module Detector

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | ReYMeN ajan (otonom döngü) + geliştirici (manuel) |
| **Ne?** | Projedeki duplicate/drift modülleri AST ile tespit eder |
| **Nerede?** | `scripts/duplicate_module_detector.py` |
| **Ne Zaman?** | Her cycle başında (cron: 06:00) + manuel talimatla |
| **Neden?** | Zamanla oluşan mimari sapmaları erken yakalamak |
| **Nasıl?** | Aynı basename'li .py'leri grupla → AST ile fonksiyon setlerini çıkar → farklı olanları raporla |

## Kullanım

```bash
# Tüm projeyi tara
python scripts/duplicate_module_detector.py

# Belirli bir entry point ile
python scripts/duplicate_module_detector.py . main.py
```

## Çıktı Formatı

```
⚠️  N drift bulundu:

🎯 once_hafiza.py (risk: YÜKSEK)
   reymen/cereyan/once_hafiza.py ← CANLI YOL
      eksik fonksiyonlar: ...
   reymen/sistem/once_hafiza.py
      eksik fonksiyonlar: ...
```

## Cron

```bash
cronjob action='create' schedule='0 6 * * *' \
  name='duplicate-module-detector-daily' \
  script='duplicate_module_detector.py' no_agent=True repeat=30
```

## İlişkili

- `scripts/duplicate_module_detector.py`
- `reymen/.ReYMeN/decisions.md`
- Skill: `devops/pipeline-redundancy-check`
