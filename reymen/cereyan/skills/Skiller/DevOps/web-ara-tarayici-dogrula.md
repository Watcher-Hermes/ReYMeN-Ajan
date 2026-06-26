---
name: web-ara-tarayici-dogrula
description: Web'de ara + tarayıcıda doğrula + sonucu göster — kullanıcı "bir bilgiye ulaşmak için tarayıcı kullanılır" dediğinde
category: workflow
version: 1.0.0
triggers:
  - tarayıcı kullan
  - tarayıcıda doğrula
  - bilgiye ulaşmak için tarayıcı
---

# Web Ara + Tarayıcı Doğrula

## 5N1K

| Alan | Açıklama |
|------|----------|
| **Kim** | ReYMeN — kullanıcı bir bilgiyi tarayıcı ile doğrulatmak istediğinde |
| **Ne** | Web araması yap, en güvenilir kaynağı tarayıcıda aç, sonucu formatla |
| **Nerede** | Terminal → web_search → browser_navigate |
| **Ne Zaman** | Kullanıcı "tarayıcı kullan", "tarayıcıda aç", "bir bilgiye ulaşmak için tarayıcı kullanılır" dediğinde |
| **Neden** | Web snippet'leri bazen yetersiz/yanlış olabilir; tarayıcı anlık ve doğru bilgi verir |
| **Nasıl** | Aşağıdaki adımlar |

## Adımlar

1. `web_search(sorgu, limit=3)` — 3 kaynak getir
2. En güvenilir kaynağı seç (haber/resmi site > blog/forum)
3. `browser_navigate(url)` — tarayıcıda aç
4. Sayfa yüklendikten sonra snapshot'tan veriyi oku
5. Tablo formatında kullanıcıya göster + kaynak belirt

## Örnek

```
Kullanıcı: "Londra hava sıcaklığını tarayıcıda bul"
1. web_search("Londra hava durumu bugün")
2. NTV/AccuWeather sayfasını seç
3. browser_navigate(url)
4. snapshot'tan sıcaklık bilgisini al
5. Tablo: Londra — Az Bulutlu, 35°C / 19°C
```

## Pitfall

- Bot tespiti olursa farklı bir site dene
- Sayfa çok büyükse `browser_snapshot(full=false)` kullan
- İlk snapshot'ta veri yoksa `browser_scroll(down)` dene
