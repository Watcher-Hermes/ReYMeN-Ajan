---
name: gorev-standart-sablonu
description: >-
  Marko/Q!'nun görev standardı şablonu. Her görevde 7 maddelik yapı:
  tanım, kanıt standardı, bitiş kriteri, self-check, eksik kalırsa,
  süre sınırı, kalıcı kayıt.
---

# Görev Standart Şablonu

## 7 Maddelik Yapı

Her görevde aşağıdaki yapıyı kullan. Eksiksiz uygula.

---

### 1. GÖREV TANIMI

```
GÖREV: [ne yapılacak]
[normal görev tanımı]
```

### 2. KANIT STANDARDI (zorunlu)

Her adım için ÖZET değil HAM ÇIKTI iste:
- Kod değişikliği → diff veya grep çıktısı
- Test → komutun ham terminal çıktısı
- Dosya oluşturma → ls -la + cat çıktısı

"✅ tamamlandı" yazmak yeterli değil, ham kanıt olmadan kabul edilmez.

### 3. BİTİŞ KRİTERİ (net, sayılabilir)

Görev şu N koşul karşılanınca biter:
1. [koşul 1 + nasıl kanıtlanacağı]
2. [koşul 2 + nasıl kanıtlanacağı]

Hepsi karşılanmadan "tamamlandı" denemez.

### 4. SELF-CHECK ADIMI (en kritik)

Tamamladığını düşündüğün anda, KENDİ KENDİNE şunu sor ve cevapla:

> "Bu kanıt, başka biri (insan) bağımsızca çalıştırsa AYNI sonucu verir mi? Yoksa sadece benim yorumuma mı dayanıyor?"

Eğer cevap "sadece yorumuma dayanıyor" ise, henüz bitmedi — ham komutu çalıştır, çıktısını kaydet.

### 5. EKSİK KALIRSA (kaçamak yasağı)

3/N koşul karşılanmadıysa, "büyük ölçüde tamamlandı" gibi yumuşatma YASAK. Net yaz:
- "X/N karşılandı"
- "Eksik: [...]"
- "Sebep: [...]"

### 6. SÜRE/CYCLE SINIRI

Bu görev en fazla [N] cycle içinde bitmeli. Süre dolarsa, nerede kaldığını decisions.md'ye kaydet, durma sebebini yaz.

### 7. KALICI KAYIT (otomatik)

Görev bitince (başarılı ya da eksik), şu üçünü otomatik yap:
1. `decisions.md`'ye sonucu ekle (silme, append)
2. Eğer tekrar oluşabilecek bir hata kalıbıysa → SKILL.md'ye kural ekle
3. Bir sonraki cycle bunu otomatik kontrol etsin diye "doğrulama script'i" varsa, onu cycle başında çalıştırmayı skill'e yaz

## Kullanım

Bir göreve başlarken bu skill'i yükle ve 7 maddeyi doldur.
