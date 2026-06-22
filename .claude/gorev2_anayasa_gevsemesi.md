# GÖREV 2: AnayasaDenetçi'yi Gevşet

## Hedef
`anayasa_denetci.py`'deki `AnayasaDenetci.denetle()` metodu her görev sonunda 10 anayasal ilkeye göre kontrol yapıyor. Basit sorularda (selamlaşma, "merhaba", "nasılsın", saat kaç, basit soru-cevap) bu kontrol gereksiz ve yanlış pozitif üretebiliyor.

## Yapılacaklar

Dosya: `/c/Users/marko/OneDrive/Desktop/Reymen Proje/hermes_projesi/anayasa_denetci.py`

### A) Basit soru tespiti ekle

`AnayasaDenetci` class'ına `_basit_soru_mu(hedef: str) -> bool` metodu ekle. Şu kalıpları tespit etsin:
- 5 kelimeden kısa sorular
- Selamlaşma: "merhaba", "selam", "hey", "naber", "nasılsın", "iyi misin"
- Basit komutlar: "saat kaç", "tarih", "bugün günlerden ne"
- Kısa cevaplar: "teşekkürler", "sağ ol", "tamam", "anladım"

### B) `denetle()` metodunu güncelle

`denetle()` çağrıldığında önce `_basit_soru_mu(hedef)` kontrolü yap. Eğer basit soruysa:
```python
if self._basit_soru_mu(hedef):
    return (True, cevap)  # Direkt geç, denetleme yapma
```

### C) İhlal eşiğini düşür

Mevcut prompt çok katı. `_ELESTIRI_SISTEM` prompt'una şu uyarıyı ekle:
"Sadece GERCEK ihlallerde uyar. Kullanıcıya yardım etmek, proje dosyalarını taramak, kod önermek gibi normal işlemler ihlal değildir."

## Test
```python
cd /c/Users/marko/OneDrive/Desktop/Reymen\ Proje/hermes_projesi
python -c "
from anayasa_denetci import AnayasaDenetci
ad = AnayasaDenetci(aktif=True)

# Basit sorular direkt gecmeli
onay, sonuc = ad.denetle('merhaba', 'Merhaba! Size nasıl yardımcı olabilirim?')
assert onay == True, f'Basit soru gecmeli: {sonuc}'
print('TEST 1 GECTI: Selamlasma')

onay, sonuc = ad.denetle('saat kac', 'Saat 14:30')
assert onay == True, f'Saat sorusu gecmeli: {sonuc}'
print('TEST 2 GECTI: Basit soru')

# Gercek isler yine denetlenmeli
onay, sonuc = ad.denetle('sistem dosyalarini sil', 'rm -rf /', revize_et=False)
print(f'TEST 3: Riskli islem tespiti: onay={onay}')
assert onay == False or 'IHLAL' in sonuc
print('TUM TESTLER GECTI')
"
```
