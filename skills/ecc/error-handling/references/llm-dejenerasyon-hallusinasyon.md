# LLM Çıktı Dejenerasyonu & Hallüsinasyon Önleme

## Anti-Hallüsinasyon Prompt Kalıpları

### KURAL: "Asla bilmiyorum deme" YASAK

Web araması ile zenginleştirilmiş LLM sistemlerinde şu talimatlar **TEHLİKELİDİR**:

```markdown
❌ "Bilmiyorum deme"
❌ "Gerçek zamanlı verilere erişimim yok deme"
❌ "KESINLIKLE kullan"
❌ "MUTLAKA web_search_tool kullan"
```

Bu talimatlar modeli **uydurmaya zorlar**. Web sonucu yoksa veya yetersizse, model boşlukları doldurmak için yanlış veri üretir.

### DOĞRU Kalıp: Koşullu Kurallar

```markdown
✅ "Eğer GUNCEL WEB ARAMA SONUCLARI verildiyse, o veriyi kullanarak cevap ver."
✅ "Web sonucu verilmediyse ve elinde güncel veri yoksa,
    'Elimde güncel veri yok, web araması yapılması gerekiyor' de."
✅ "Eğer sonuçta kesin fiyat/veri varsa onu yaz."
✅ "Eğer sonuç yetersizse, 'Web araması yapıldı ama kesin sonuç bulunamadı' de."
✅ "Asla uydurma fiyat/veri/tarih verme."
```

### Mantık
| Durum | Doğru davranış |
|:------|:---------------|
| Web sonucu **var** + kesin veri | Kullan, raporla |
| Web sonucu **var** ama yetersiz | "Arama yapıldı ama kesin sonuç bulunamadı" |
| Web sonucu **yok** | "Elimde güncel veri yok" |
| Hiçbir durumda | Uydurma veri VERME |

---

## Web-Augmented Prompt Düzenleme

### Pitfall: Çift Ekran (Duplicate Context)

Web sonuçları prompt'a **iki kez** eklenebilir:
1. Formatlı haliyle (`## GUNCEL WEB ARAMA SONUCLARI`)
2. Raw JSON haliyle (`## Ek Bilgi` → `{"web_arama_sonucu": "..."}`)

Bu modelin kafasını karıştırır. Çözüm:

```python
web_sonucu_eklendi = False
if ek_bilgi and "web_arama_sonucu" in ek_bilgi:
    # Formatlı hali ekle
    parcalar.insert(0, web_blok)  # EN ÜSTE — model önce görsün
    web_sonucu_eklendi = True

if ek_bilgi:
    if web_sonucu_eklendi:
        # web_arama_sonucu HARIÇ diğer bilgileri ekle
        diger = {k: v for k, v in ek_data.items() if k != "web_arama_sonucu"}
        if diger:
            parcalar.append(f"## Ek Bilgi\n{json.dumps(diger)}")
    else:
        parcalar.append(f"## Ek Bilgi\n{ek_bilgi}")
```

### Pitfall: Web Sonucu Prompt Sonunda

Web sonuçları prompt'un **en sonuna** eklenirse, model bunları görmeyebilir (uzun sistem promptu varsa). Çözüm: `parcalar.insert(0, web_blok)` ile EN ÜSTE ekle.

---

## LLM Çıktı Dejenerasyon Tespiti

### Belirtiler

| Dejenerasyon Tipi | Örnek | Tespit |
|:------------------|:------|:-------|
| Tek karakter tekrarı | `因为因为因为...` | `(.)\1{19,}` regex |
| Kelime tekrarı | `çünkü çünkü çünkü...` | `(\b\w{2,}\b)(?:\s+\1){4,}` regex |
| CJK spam (Türkçe bağlamda) | `因为因为因为` | `[\u4e00-\u9fff]` > 10 karakter |
| Çok uzun yanıt | 4000+ karakter | `len(icerik) > MAX_YANIT_UZUNLUK` |
| Anlamsız karışım | Türkçe + Çince + rastgele | Normal karakter oranı < %50 |

### Tespit Kodu

```python
import re

def cikti_dogrula(icerik: str) -> dict:
    """LLM çıktısını doğrula."""
    if not icerik or not icerik.strip():
        return {"gecerli": False, "sorun": "Boş yanıt"}

    # 1. Tek karakter tekrarı
    if re.search(r'(.)\1{19,}', icerik):
        return {"gecerli": False, "sorun": "Tek karakter tekrarı"}

    # 2. Kelime tekrarı
    if re.search(r'(\b\w{2,}\b)(?:\s+\1){4,}', icerik):
        return {"gecerli": False, "sorun": "Kelime tekrarı"}

    # 3. CJK spam (Türkçe/İngilizce bağlamda)
    cjk = re.findall(r'[\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff]', icerik)
    if len(cjk) > 10:
        return {"gecerli": False, "sorun": "CJK spam"}

    return {"gecerli": True, "sorun": None}
```

### Çıktı Doğrulama Entegrasyonu

```python
# Hızlı yol (sohbet/bilgi) — doğrulama sonrası ReAct'e düş
yanit = provider.uret(prompt, mesajlar)
sonuc = cikti_dogrula(yanit)
if not sonuc["gecerli"]:
    log.warning("Bozuk çıktı: %s — ReAct'e düş", sonuc["sorun"])
    tip = "karmasik"  # ReAct döngüsüne düş
```

---

## Hallüsinasyon Risk Kontrol Listesi

Web-augmented LLM sistemi kurarken:

- [ ] "Bilmiyorum deme" talimatı YOK — koşullu kurallar kullan
- [ ] Web sonuçları EN ÜSTE ekleniyor (prompt sonunda değil)
- [ ] Raw JSON tekrarı yok (formatlı + raw ayrı ayrı eklenmiyor)
- [ ] Çıktı doğrulama var (CJK spam, tekrar tespiti)
- [ ] Web sonucu yoksa model "elimde veri yok" diyebilir (zorlanmıyor)
- [ ] Cache hit sonrası içerik doğrulama (bozuk/truncated kontrolü)
