# AI Agent Çalışma Yönergeleri

## 1. Her Oturumun Başında

Önce `memory_bank.md` dosyasını oku ve projenin mevcut durumunu anla. Sonra bana şunları söyle:
- Son ne yapıldı?
- Şu an hangi özellikler çalışıyor?
- Yarım kalan veya bilinen sorun var mı?

Anladıktan sonra "Hazırım, devam edebiliriz" de.
**Onayımı almadan hiçbir kod yazma.**

## 2. Yeni Özellik Eklerken

```
[ÖZELLİK]: ...buraya yaz...
```

Kodu yazmadan önce şunları listele:
1. Hangi dosyalara dokunacaksın?
2. Bu değişiklik hangi mevcut özellikleri etkileyebilir?
3. Risk taşıyan yerler neresi?

Onayımı aldıktan sonra yaz. Bitince:
- Ne değiştirdiğini özetle
- Test etmemi gereken eski özellikleri listele
- `memory_bank.md`'yi güncelle

## 3. Bug Düzeltirken

```
[BUG]: ...buraya yaz...
```

Düzeltmeden önce:
1. Bu bug neden oluşuyor, kök sebebi nedir?
2. Düzeltmek için hangi dosyalara dokunacaksın?
3. Bu düzeltme başka neyi bozabilir?

Düzelttikten sonra:
- **Testi geçirmek için test kodunu değiştirme**
- Yaptığın değişikliği satır satır açıkla
- `memory_bank.md`'yi güncelle

## 4. Kod Yazma/Değiştirme Öncesi

Kodu yazmadan veya değiştirmeden önce yapılması gerekenler:
- Mevcut yapıyı anla (dosyaları oku)
- Değişikliğin etkilerini analiz et
- Riskleri belirle
- Onay al

**Bu yönergelere uymayan hiçbir kod yazılmaz.**
