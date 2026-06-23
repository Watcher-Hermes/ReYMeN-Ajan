# Mimari Zayıflık #1 — Hafıza Katmanı Parçalanması

## Keşif Tarihi: 2026-06-23

### Sorun

ReYMeN'de 3 ayrı hafıza sistemi yan yana çalışıyor, her biri farklı API ve DB kullanıyor:

| Dosya | API | DB | Kullanım |
|:------|:----|:---|:---------|
| `reymen/cereyan/once_hafiza.py` | `kaydet()`, `ara()`, `isle()` (modül-seviye) | `.ReYMeN/ogrenmeler.db` | Ana hafıza — en çok kullanılan |
| `reymen/sistem/once_hafiza.py` | `OnceHafiza` class (OOP) | Aynı DB? Farklı tablo? | conversation_loop.py import ediyor |
| `reymen/hafiza/gorev_hafiza.py` | `gorev_hafiza()` | Muhtemelen farklı | Görev sonrası hafıza genişletme |

### Etkisi

- Aynı veri 3 farklı yoldan yazılabilir → tutarsızlık
- Bir yere yazılan hafıza diğer sistemden okunamayabilir
- Bakım yükü: 3 kodu da güncellemek gerek
- Hata ayıklama: hangi sistemin hangi veriyi yazdığını takip etmek zor

### Düzeltme Önerisi

Tüm hafıza işlemlerini `reymen/cereyan/once_hafiza.py` altında birleştir:
1. `reymen/sistem/once_hafiza.py` → `reymen/cereyan/once_hafiza.py`'ye import wrapper yap
2. `reymen/hafiza/gorev_hafiza.py` → aynı DB'yi kullan, yeni tablo/tablo yoksa wrapper
3. conversation_loop.py → direkt `cereyan.once_hafiza`'yı import et

### Statü: ⚠️ AÇIK — düzeltilmesi önerilir
