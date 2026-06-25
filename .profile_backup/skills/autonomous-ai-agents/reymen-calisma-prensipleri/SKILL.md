---
name: reymen-calisma-prensipleri
title: "ReYMeN Çalışma Prensipleri ve Yanıt Metodolojisi"
description: "ReYMeN'in karar alma, yanıt formatlama, araç kullanımı, batch iş akışı, skill organizasyonu, ekip hafızası yönetimi ve gateway crash recovery için framework. No Goblins, Cave Mode, Karar Döngüsü, Side Quest, Status Line, Batch Auto-Proceed, Büyük Ölçekli Organizasyon."
version: 1.3.0
tags: [reymen, calisma-prensipleri, yanit-format, karar-dongusu, metodoloji]
audience: agent
---

# ReYMeN Çalışma Prensipleri ve Yanıt Metodolojisi

ReYMeN'in kazan sağlama odaklı çalışma prensipleri. Her görevde uygulanır.

---

## 1. No Goblins — Gereksiz İş Yapma

Temel disiplin kuralı. Diğer tüm kurallar No Goblins olmadan anlamsız.

| Yap | Yapma |
|:----|:------|
| Direkt ilerle | Fazla soru sorma |
| Gerekeni yap, dur | Sapma, konuyu dağıtma |
| Araç kullan, anlatma | Uzun açıklama, özür, yorum |

**Tetikleyici:** Herhangi bir görevde "acaba şunu da eklesem mi?" düşüncesi → DUR. Gerekli değilse ekleme.

**Kritik alt kural — Önce veriyi/kuralları topla, yorum katma:**
Soruyu duyunca kafadan formül üretme. Önce execute_code brute force, web_search canli veri, read_file icerik ile ham veriyi topla. Tablo halinde sun. Sonra direkt cevap ver. Genelleme yapma, uydurma formül üretme.

**Pitfall — analiz/optimizasyon tuzaklari:**
Matematik/mantik sorusunda kafadan cozmeye calisma. Kullanici kurallari verir, sen execute_code ile brute force yap, tum olasiliklari tablola, cevabi isaretle. Bu kanit da uretir.

---

## 2. Cave Mode (Concise Mode) — Kısa ve Öz Cevap

Uzun süslü cevaplar yasak. Direkt söyle, yağlama/sarma/okşama yok.

| Durum | Format |
|:------|:-------|
| Fiyat/veri sorusu | Kiral38 formatı: emoji başlık + Kaynaklar tablosu (URL + fiyat) + Fiyat Uyumu satırı + Ortalama |
| Analiz sorusu | Emoji başlık + kısa tablo + sonuç |
| Matematik/mantık | execute_code brute force + tablo + cevap |
| Karar sorusu | decisions.md'ye kaydet + özet |
| **5N1K yapısal çıktı** | Ağaç formatı: `├── 🧩 ecc 392` (emoji + ad + sayı) |
| **Katalog/liste** | Tablo formatı: `| # | Başlık | Sayı |` |
| **Bot teşhis/onarım** | Emoji başlık + Kontrol tablosu + bulgu + çözüm adımları (kod blokları) |

**Yasak:** Teknik analiz, gereksiz grafik yorumu, gorunuse gore, acikcasi gibi dolgu ifadeleri, süslü cümleler, açıklama paragrafları.

**🔴 KRİTİK — Cave Modu 'açıklama' yasağı:**
- Kullanıcı "nasıl" demediyse NASIL anlatma, direkt yap/söyle
- "Ne yapmam gerek?" sorusuna çözüm adımlarını SIRALA, açıklama KATMA
- Her cevap = sorunun direkt karşılığı + istenen format. Ara metin, giriş, yorum EKLEME

**Kiral38 Format Detayi (Canli Fiyat/Veri):**
Emoji baslik + Kaynaklar tablosu + Fiyat Uyumu satiri + Ortalama.
Ornek icin references/yanit-format-ornekleri.md dosyasina bak.

## 2b. 5N1K Ağaç Formatı — Yapılandırılmış Hiyerarşik Çıktı

Kullanıcı "Bu formatta cevap ver, kalıp dışına çıkma" dediğinde:

| Kural | Açıklama |
|:------|:---------|
| **Emoji başlık** | Her ana başlık emoji ile başlar (`📊`, `🧩`, `🤖`) |
| **Ana/alt hiyerarşi** | `├──` ağaç dalları, 2 seviye maks |
| **Sayı sağa yaslı** | `{ad:20s} {sayi:4d}` formatı |
| **Alt başlık parantezi** | `(alt1:n, alt2:m)` ek bilgi |
| **Seçenek: tablo** | Ağaç yerine sütunlu tablo da kullanılabilir |

**Tetikleyici:** Kullanıcı "Bu formatta ver" / "kalıp dışına çıkma" / "şu formatta cevap ver" dediğinde.
**Pitfall:** Kullanıcının istediği formatı (tablo vs ağaç) net anla — ikisini birden sunma, sadece isteneni ver.

---

## Karar Döngüsü — decisions.md + kazanimlar.md

Her önemli karardan sonra 3 soru sor ve `decisions.md`'ye kaydet.
**Ayrıca:** Her session sonunda tüm kazanımlar (kod değişiklikleri, cron job'lar, config ayarları) `.ReYMeN/notes/kazanimlar_YYYY-AA-GG.md`'ye yazılır. decisions.md kararları, kazanimlar.md ise yapılan tüm değişiklikleri tutar.

```
## Karar #N — [Başlık]

**Tarih:** ...
**Bağlam:** ...

### 1. Ne yaptın?
[eylem]

### 2. Neden?
[gerekçe]

### 3. Alternatif düşündün mü?
[diğer seçenekler + neden seçilmedi]
```

**Tetikleyici:** Yeni bir kural seçimi, framework değişikliği, önemli mimari karar.

---

## 11. Gateway Crash Recovery — Tanı + Onarım

Gateway düştüğünde (bot yanıt vermiyor) hızlı tanı ve onarım akışı.

### 11.1. Tanı — Ne Kadar Ölü?

| Kontrol | Komut | Anlamı |
|:--------|:------|:-------|
| Process | `ps aux | grep -i "gateway"` | PID yoksa gateway çökmüş |
| State | `cat profiles/{profil}/gateway_state.json` | "running" dese bile PID ölmüş olabilir |
| Lock | `cat profiles/{profil}/gateway.lock` | Stale PID var mı? |
| Status | `hermes gateway status --profile {profil}` | Scheduled Task + PID birlikte gösterir |
| Log | `tail -20 profiles/{profil}/logs/gateway.log` | En son hata ne? |
| Token | `grep TELEGRAM_BOT_TOKEN profiles/{profil}/.env` | Token geçerli mi? BotFather'dan kontrol |

### 11.2. Bilinen Çökme Sebepleri

| Sebep | Belirti | Çözüm |
|:------|:--------|:------|
| **Token geçersiz** (InvalidToken) | `"The token was rejected by the server"` | BotFather → yeni token → .env'ye yaz |
| **PowerBI MCP çökmesi** | MCP stdout'ta non-JSON satır + "No messaging platforms enabled" | PowerBI MCP'yi config'den kaldır (`hermes config set --profile X mcp_servers {}`) |
| **Runtime lock conflict** | `"Another gateway instance is already running"` | Var olan PID kullanılır. Yeni başlatma reddi NORMAL |
| **Stale lock** | PID yok ama lock var | `echo "{}" > gateway.lock` ile üzerine yaz |
| **Global lock** | `"Another gateway instance is already running (PID X)"` | `echo "{}" > ~/AppData/Local/hermes/gateway.lock` |
| **Birden çok profil** | reymen varsa kiral38 başlayamaz | İkinci profil için gateway'i ayrı başlat. Çakışma varsa --replace flag'ini dene |

### 11.3. Tam Onarım Akışı (Token + Lock + MCP)

```bash
# 1. Token'ı güncelle (BotFather'dan yeni token alındıysa)
sed -i "s|TELEGRAM_BOT_TOKEN=.*|TELEGRAM_BOT_TOKEN=YENI_TOKEN|" ~/AppData/Local/hermes/profiles/{profil}/.env

# 2. Stale lock'ları temizle
echo "{}" > ~/AppData/Local/hermes/profiles/{profil}/gateway_state.json
echo "reset" > ~/AppData/Local/hermes/profiles/{profil}/gateway.lock

# 3. Eğer varsa global lock'u temizle
echo "{}" > ~/AppData/Local/hermes/gateway.lock

# 4. Eğer MCP server gateway'i çökertiyorsa (log'da MCP JSON parse error varsa)
#    config.yaml'dan powerbi MCP'yi kaldır
patch önce: "mcp_servers:\n  powerbi:\n    command: powerbi-modeling-mcp\n    args: [\"--start\"]"
patch sonra: ""  # (boş, tamamen kaldır)

# 5. Gateway'i başlat
hermes gateway run --profile {profil} --replace 2>&1

# 6. Doğrula
sleep 12 && grep -E "✓ telegram connected\|connected" ~/AppData/Local/hermes/profiles/{profil}/logs/gateway.log
```

### 11.4. .env Dosyası Bozulursa (Koruma)

.env dosyası yanlışlıkla silinir/bozulursa, **çalışan başka bir profilin** .env'sini kopyala, sadece token'ı değiştir:

```bash
# Çalışan profilden kopyala
cp ~/AppData/Local/hermes/profiles/calisan_profil/.env ~/AppData/Local/hermes/profiles/bozuk_profil/.env

# Token'ı değiştir (Python ile, sed özel karakterlerde hata verebilir)
python3 -c "
import os
env_path = os.path.expanduser('~/AppData/Local/hermes/profiles/bozuk_profil/.env')
with open(env_path, 'rb') as f:
    content = f.read()
content = content.replace(b'ESKI_TOKEN', b'YENI_TOKEN', 1)
with open(env_path, 'wb') as f:
    f.write(content)
"
```

### 11.5. Önleyici — PowerBI MCP Sorunu

`powerbi-modeling-mcp` gemini 0.5.0-beta sürümü stdout'a non-JSON satırlar basar:
```
Detected platform: win32, architecture: x64
Using @microsoft/powerbi... version: 0.5.0-beta.10
```
Bu satırlar MCP client'ın JSON-RPC ayrıştırıcısını çökertir → "No messaging platforms enabled".

**Çözüm:** Gateway'i çalıştırmadan önce powerbi MCP'yi config'den kaldır. Sadece kiral38/default profillerinde — reymen'de sorunsuz çalışabilir.

**Tetikleyici:** Gateway log'unda `"Failed to parse JSONRPC message from server"` + `"No messaging platforms enabled"`

## 12. Side Quest → Sub-Agent Kuralı

Ana göreve dahil olmayan yan görevleri otomatik olarak sub-agent'a devret.

| Ana Görev | Side Quest (Sub-Agent) |
|:----------|:-----------------------|
| Kod yazma | Codex cross-check, güvenlik taraması |
| Rapor hazırlama | Veri doğrulama, kaynak kontrolü |
| Hata ayıklama | Alternatif çözüm araştırması |

**Kural:** Ana thread'i kirletme. Yan isler sub-agent'da paralel yurutsun.

**Pratik ornek — Gateway crash recovery:**
Kiral38 bot gateway'i olmus halde bulundugunda (PID yok ama state "running" diyor):
1. Yeni PID kontrol et → yoksa
2. `hermes -p kiral38 gateway install` ile Scheduled Task kur
3. UAC prompt'unda otomatik Allow Once sec
4. Bot canli mi kontrol et

Bu islem dogrudan ana thread'de yapilir (Side Quest degil, gateway aksiyonu). Side Quest ornegi: bot yanit verirken sen ayni anda baska bir sey yapiyorsan, bot beklemesi sub-agent'a at.

---

## 5. Status Line — Maliyet Takibi

Terminal altında veya cevap sonunda göster:
- Kalan limit / context window doluluk
- API maliyet tahmini (key kullansaydım ne kadar öderdim)
- Adım sayısı / geçen süre

**Sadece önemli olduğunda göster.** Her cevapta status line israf.

---

## Araç Kullanım Önceliği

Her soruda ÖNCE araç kullan, hafızadan/formül üretme:

| Soru Türü | Araç | Neden |
|:----------|:-----|:------|
| Fiyat/veri | `web_search` | Canlı veri, güncel |
| Matematik/mantık | `execute_code` brute force | Doğru sonuç, kanıt |
| Dosya içeriği | `read_file` / `search_files` | Gerçek içerik |
| Kod çalıştırma | `terminal` | Gerçek çıktı |

**Kural:** Kafadan formül üretme, yorum katma. Önce tara, sonra cevap ver.

### Araç Seçimi: Python Kodu için `execute_code` Öncelikli

Kullanıcı bir Python snippet'i verdiğinde veya Python ile çözülebilecek bir hesaplama/mantık sorusu sorduğunda:

| Araç | Ne Zaman | Neden |
|:-----|:---------|:------|
| **`execute_code`** | ✅ **PRIMARY** — Python snippet çalıştırma, brute force, veri analizi | Doğrudan Python, `hermes_tools` var, timeout yok, kanıt üretir |
| `terminal` | ❌ Python snippet için kullanma | Gereksiz shell wrapper, `python -c` tırnak sorunları |
| `terminal` | Sadece shell komutları için (git, ls, curl, pip) | Shell gerektiren işler |

**Tetikleyici:** Kullanıcı Python kodu verir (`şunu çalıştır: import os...`) veya brute force gereken matematik/mantık sorusu.

**Kural:**
1. Kullanıcının verdiği Python snippet'ini direkt `execute_code(code=...)` içine yapıştır
2. `import`'ları olduğu gibi bırak, `hermes_tools`'u ihtiyaç varsa ekle
3. Sonucu doğrudan göster — önce `print()` çıktısı, yorum sonra

**⚠️ Kritik — Önce 3 yöntemle kontrol et (skill: reymen-kontrol-kurali):**
"X yok" demeden önce şu 3 yöntemi dene:
1. Dosya sistemi (`find /c/ -iname "*hedef*"`)
2. Process (`tasklist | grep -i "hedef"`)
3. Store/Path (`where hedef`, `Get-StartApps`)
Detaylı talimat ve örnek için `reymen-kontrol-kurali` skill'ini yükle.

**⚠️ Windows cron — bash yok, .py kullan (skill: reymen-kontrol-kurali Kural 4):**
Cron job script'i `.sh` olursa Windows'ta patlar. Her zaman `.py` kullan.
Detay: `references/cron-no-agent-pattern.md`

## 6. Hafıza-Öncelikli Akış (3 İyileştirme) — Önce Hafızaya Bak

Eski akış (geçersiz): `Görev → Dene → Sonuç → Kaydet` 
Varsayılan LLM akışı: `Görev → LLM → Dene → LLM → Sonuç → LLM → Kaydet` (her adım LLM)
ReYMeN akışı (aktif): `Görev → HAFIZA → CACHE → LLM (son çare)`

```
Görev gelir
  ↓
① İYİLEŞTİRME: ZORUNLU HAFIZA KONTROLÜ (guven_skoru > 0.8?)
  ├─ EVET → direkt döndür, 0 LLM çağrısı, %60 maliyet düşüşü
  │         Kullanım sayısını güncelle (guncelle_son_kullanim)
  └─ HAYIR → devam
              ↓
② İYİLEŞTİRME: CACHE KONTROLÜ (ONCELIK_CACHE — 12 pattern)
  ├─ EVET → selam/teşekkür/bye direkt döndür, 0 LLM çağrısı
  └─ HAYIR → devam
              ↓
③ EN SON LLM (DeepSeek) — her turda 1 API call
  ├─ Maks 90 tur (IterationBudget)
  ├─ Maks 3 exponential backoff retry (MAX_API_RETRY=3)
  ├─ 3 ardışık hata → KALICI circuit breaker (CIRCUIT_BREAKER_KALICI=True)
  │    └─ Kullanıcıya: "3 deneme hakkiniz doldu" → dur
  └─ Takılma dedektörü: 3x aynı eylem → break
```

**Çıkış Koşulları (8 adet — mekanik, LLM kararı değil):**
| # | Koşul | Kod | 
|:-:|:------|:----|
| 1 | guven_skoru > 0.8 | Hafızadan direkt, LLM yok |
| 2 | Cache eşleşmesi | Selam/teşekkür direkt döndür |
| 3 | budget(90) doldu | IterationBudget.devam_etmeli_mi()=false |
| 4 | GOREV_BITTI | LLM metinde "bitti" dedi |
| 5 | tool.tamamlandi=true | Tool "bitti" sinyali |
| 6 | Takılma (3x) | Aynı eylem 3x tekrar |
| 7 | Circuit breaker (3x) | 3 ardışık hata, kalıcı dur |
| 8 | Ctrl+C | Kullanıcı iptali |

**Araç Seçimi (Tool Öncelik):**
```
SABİT LİSTE (~30-64 araç, system prompt'ta)
├── Hepsi her zaman kullanılabilir
├── LLM hangilerini kullanacağına karar verir
├── Dinamik seçim: YOK (sabit liste)
├── Plugin modüller: 80+ plugin dinamik yüklenir
└── check_fn: Ortama göre filtreleme (örn. Windows'ta Linux tool'larını gizle)
```

**ReYMeN vs Varsayılan LLM Karşılaştırması:**
| Boyut | ReYMeN | Varsayılan LLM (Hermes) |
|:------|:-------|:------------------------|
| **Mimari** | Mühendislik: hafıza öncelikli, LLM son çare | LLM merkezli: her adım LLM |
| **Maliyet** | Düşük (cache + LLM'siz kararlar) | Yüksek (her şey LLM'den geçer) |
| **Hız** | Hızlı (cache'ten direkt) | Yavaş (LLM her turu bekler) |
| **Tutarlılık** | Yüksek (SQLite, kurallı) | Düşük (LLM rastgele) |
| **Esneklik** | Düşük (kurallar kısıtlar) | Yüksek (LLM her şeyi yapabilir) |
| **Unutkanlık** | Az (SQLite kalıcı — dünkü bilgi bugün kullanılır) | Çok (yeni oturumda her şey unutulur) |
| **Retry garantisi** | Var (3 retry + circuit breaker) | Yok (LLM karar verir, sınırsız dener) |
| **Tool çeşitliliği** | Çok (50+ sabit + runtime + 80+ plugin) | Az (system prompt'taki kadar) |
| **Cross-oturum** | ✅ Dünkü bilgiyi bugün kullanır | ❌ Yeni oturumda her şeyi unutur |

**ReYMeN'in en büyük avantajı:** Cross-oturum hafıza. Varsayılan LLM bir sonraki oturumda her şeyi unutur, aynı maliyeti tekrar öder. ReYMeN SQLite sorgular, 5 saniyede cevap verir, sıfır maliyet.

**Sabitler (kalıcı, her çalışmada aktif):**
```python
CIRCUIT_BREAKER_MAX_HATA = 3    # 3 ardışık hata → dur
CIRCUIT_BREAKER_KALICI = True   # otomatik açılmaz
MAX_API_RETRY = 3               # exponential backoff max deneme
TAKILMA_ESIĞI = 3               # 3x aynı eylem = takılma
ONCELIK_CACHE = {...}           # 12 pattern: merhaba, selam, teşekkür, bye vs
```

**Kod konumları:**
- `reymen/hafiza/gorev_once_kontrol.py` — 5 katmanlı ön hafıza kontrolü + isle/hafizada_ara/kaydet_isle API'leri
- `reymen/hafiza/hata_analiz.py` — 7 sınıflı hata sınıflandırma + çözüm yönetimi
- `reymen/hafiza/gorev_hafiza.py` — gorev_sonrasi_hafiza + guncelle_son_kullanim
- `.ReYMeN/hata_cozumleri.md` — Kalıcı hata-çözüm veritabanı
- `conversation_loop.py` — run_conversation(): önce hafiza, sonra cache, en son LLM

**Yeni API'ler (gorev_once_kontrol.py):**
- `isle(hedef, lambda, kategori)` — hafızaya bak → varsa döndür → yoksa çalıştır → kaydet → döndür
- `hafizada_ara(hedef, kategori)` — kategori filtresi + güven skoru + geçerlilik kontrolü
- `kaydet_isle(hedef, kategori, sonuc, basarili)` — otomatik güven skorlu kaydetme
- `cross_agent_ekle(ajan_adi, proje_yolu)` — farklı ajan hafızalarını tara

**Metadata (her kayıt):**
```json
{
  "guven_skoru": 0.85,
  "kategori": "kali/network/nmap",
  "son_kullanim": "2026-06-21 18:05",
  "gecerlilik_tarihi": "2026-12-21",
  "kullanim_sayisi": 3,
  "basari_sayisi": 3,
  "hata_sayisi": 0,
  "kayit_id": 1972
"kayit_id": 1972
}

**Pitfall:** Ön kontrol sıfır eşleşme döndürebilir. Bu durumda normal akış devam eder, sorun yok.

**Pitfall — Yeni kayıt vs güncelleme:** `gorev_sonrasi_hafiza()` her çağrıldığında YENİ kayıt açar. Aynı bilgiyi genişletiyorsan `hafiza.kayit_guncelle(kayit_id, yeni_metadata)` kullan. Yeni kayıt açma.

**🔴 KRİTİK PITFALL — `pytest --collect-only` KULLANMA:** Cron prompt'unda veya test öncesi `pytest --collect-only` KESİNLİKLE KULLANMA. Bunun yerine `compile()` ile syntax kontrolü yap.

**Pitfall — Cross-agent import:** Bir ajan başka bir ajanın hafızasını okumak istiyorsa `cross_agent_ekle()` + `cross_agent_tara()` kullan.

**Pitfall — Hafıza atlama import hatası:** ImportError sessiz geçilmez — log'da görünür.

## 7. Batch Auto-Proceed Kuralı — Sessiz Onay + Otomatik Devam

Çok adımlı batch işlerde (skill taşıma, test batch, dosya işleme) her adımda onay bekleme.

| Kural | Açıklama |
|:------|:---------|
| **Sessiz Onay** | **3 dakika** bekle, cevap gelmezse onay say |
| **Batch devam** | "Skiller tamami onaysız bitene kadar devam et" = tüm batch bitsin |
| **En mantıklı seçenek** | Belirsizlikte en mantıklı olanı seç, raporla |
| **İstisna** | Sadece tehlikeli işlemlerde (silme, overwrite) dur ve sor |

**⚠️ Pitfall — Telgraf 3 dk kuralı:** Kullanıcı "Sor sor → 3 dk bekle → Cevap gelmezse sessiz onay" dediğinde bu, batch auto-proceed'in genişletilmiş halidir. Batch devam etmeden ÖNCE bir soru sor, 3 dk bekle, cevap yoksa onay say, devam et. Bu sadece batch'te değil, TEK SORU'da da geçerli.

**⚠️ Terminal fallback — execute_code içinde terminal():** `terminal` tool'u timeout atarsa (bloke bash), `execute_code` içindeki `from hermes_tools import terminal; terminal("komut", timeout=5)` alternatif shell üzerinden çalışır. Önce bunu dene, direkt terminal işe yaramazsa execute_code'u kullan. execute_code'un da 5 dk timeout limiti vardır.

**Tetikleyici kalıpları (hepsi eşdeğer):**
- "Hepsini sırayla yap" / "Onaysız bitene kadar devam et"
- "Skiller tamami onaysız bitene kadar devam et"
- "Sessiz onaysız geçerli 2 dak bekle cevap gelmez ise en mantikli seçenek devam"
- "Her biteni test et, otomatik diğerine geç"
- "Sor sor → 3 dk bekle → Cevap gelmezse sessiz onay" (genişletilmiş: soru sor + bekle + onay say)

**Akış:**\n```\nbatch_ise_basla()\n  ├─ Her adımda: islem_yap() + rapor_ver() + 3dk_bekle()\n  ├─ Cevap gelmezse → onay_say() → sonraki_adima_gec()\n  ├─ Cevap gelirse (dur/düzelt) → kullanici_talimatini_uygula()\n  └─ Tüm batch bitince → ozet_raporu_ver()\n```

**Pitfall — Batch içinde kritik hata:** Batch'in ortasında bir adım hata verirse, dur ve raporla. "En mantıklı seçenek" hatalı adımı atlamak değil, raporlayıp devam kararını kullanıcıya bırakmaktır.

---

## 8. Büyük Ölçekli Dosya/Skill Organizasyonu

Yüzlerce/binlerce dosyayı kategorilere ayırma iş akışı.

### 8.1. Keşif Aşaması

```bash
# Dosya sayısını ve isim desenlerini analiz et
python3 -c "
import os
from collections import Counter
files = [f for f in os.listdir(skills_dir) if f.endswith('.md')]
prefixes = Counter()
for f in files:
    if '_' in f:
        p = f.split('_')[0]
    else:
        p = f.split('-')[0]
    prefixes[p] += 1
"
```

### 8.2. Duplicate Tespiti ve Budama

`full_X.md` + `X.md` ikilileri varsa:
- **`full_` öneki** = Hermes formatlı (YAML frontmatter, daha eksiksiz) → KANONİK
- **Düz `X.md`** = Kısa/eskimiş versiyon → SİLİNİR
- **Sadece biri varsa** → olduğu gibi kalır

```python
if has_full and has_normal:
    keep = full_v   # full_ versiyonu koru
    shutil.move(full_v, target_dir / base_name)
    os.remove(normal_v)
```

### 8.3. Prefix Bazlı Kategori Atama

Dosya ismindeki ön eki analiz ederek kategori belirle:

| Ön Ek | Kategori | Örnek |
|:------|:---------|:------|
| `creative_` | creative | `creative_ascii-art.md` |
| `devops_` | devops | `devops_backup.md` |
| `windows-automation_` | windows/automation | `ekran-al.md` |
| `ecc_` | ai/ecc | `ecc_accessibility.md` |
| `software-development_` | software-development | `software-development_plan.md` |

### 8.4. Misc (Sınıflandırılamayan) İçin İkinci Aşama

İsimde anahtar kelimelere göre alt kategorilere ayır:

```python
subcats = {
    'prompt-engineering': ['prompt','function-calling'],
    'agent-systems': ['agent','multi','swarm'],
    'llm-inference': ['llm','inference','vllm'],
}
```

### 8.5. Katalog Oluşturma

Her kategorideki dosya sayısını gösteren ağaç yapısında katalog dosyası (`SKILLS_KATALOG.md`) oluştur.

**Gerçek dünya (2026-06-21):** 2176 ham → 1130 organize → 30 kategori → 0 uncategorized.

**Tetikleyici:** Yüzlerce skill/dosyayı organize etme gerektiğinde.

### 8.6. Türkçe Karakter Normalleştirme (Pitfall)

Windows dosya isimlerinde Türkçe karakter (ı,ş,ü,ö,ğ,İ) olabilir. Python `os.listdir()` bunları doğru okur ama manuel eşleme yaparken Unicode normalizasyon gerekir:

```python
import unicodedata
def norm(s):
    nfkd = unicodedata.normalize('NFKD', s)
    return nfkd.encode('ASCII', 'ignore').decode().lower()

# Her zaman normalizasyon ile eşle
target = MAP.get(f) or MAP.get(norm(f))
```

**Pitfall — _2 çakışma çözümü:** Aynı hedef dosya adı varsa `_2` suffix eklenir. Bunlar elle temizlenmelidir — otomatik silme tehlikelidir.

### 8.7. Referans

Detaylı gerçek dünya uygulaması için: `references/skill-categorization-pattern.md`

---

## 9b. Hafıza 5N1K Taksonomi Sınıflandırması

Binlerce DB kaydını (ör: 1773) 5N1K (Ne? Nerede? Nasıl? Neden? Kim?) şemasına göre sınıflandırma akışı.

### 9b.1. Şema Tanımı

`ogrenmeler.db`'ye 5 sütun eklenir: `ne`, `nerede`, `nasil`, `neden`, `kim`

```sql
ALTER TABLE ogrenmeler ADD COLUMN ne TEXT DEFAULT '';
ALTER TABLE ogrenmeler ADD COLUMN nerede TEXT DEFAULT '';
ALTER TABLE ogrenmeler ADD COLUMN nasil TEXT DEFAULT '';
ALTER TABLE ogrenmeler ADD COLUMN neden TEXT DEFAULT '';
ALTER TABLE ogrenmeler ADD COLUMN kim TEXT DEFAULT '';
```

### 9b.2. 5N1K Kategori Ağacı

```
NE → Ana başlıklar: Ağ, Kod, Windows, Yaratıcı, Güvenlik, ecc, DevOps, ...
NEREDE → Platform: Windows Yerel, Hermes, GitHub, Kali VM, ...
NASIL → Yöntem: Otomatik, Video, Web, Test, Kullanıcı, ...
NEDEN → Sebep: Otomasyon, Güvenlik, Test, Hata, Öğrenme, ...
KIM → Kaynak: Windows Ajanı, Video Ajanı, ReYMeN, Kullanıcı, Kali, ...
```

### 9b.3. Sınıflandırma Stratejisi

| Aşama | Yöntem | Hedef |
|:------|:-------|:------|
| 1. Keşif | `GROUP BY kategori` | Mevcut dağılımı gör |
| 2. Keyword eşleme | `if kw in text.lower()` | 5N1K etiketle |
| 3. Alt başlık yükseltme | `UPDATE SET ne=alt_baslik WHERE ne='ai/ecc'` | Büyük alt kümeleri ana başlık yap |
| 4. "Diğer" avı | Art arda keyword ekle | Sıfır uncategorized |
| 5. Turkish normalize | `unicodedata.normalize('NFKD', s)` | Türkçe karakter sorunlarını çöz |

### 9b.4. Alt Başlık → Ana Başlık Promosyon Kriteri

Bir alt başlık (`ai/ecc`) şu durumda ana başlığa (`ecc`) yükseltilir:
- **10+ kayıt** → yeni ana başlık olmayı hak eder
- **Bağımsız anlamı var** → kendi başına bir konu alanı
- **Örnek:** `ai/ecc:392` → `ecc`, `ai/prompt:51` → `prompt`, `ai/nlp:49` → `nlp`

### 9b.5. Kod Kalıbı

```python
# Keyword tabanlı sınıflandırma
NE_RULES = {
    "ai/ecc": ["ecc", "edge case", "agentic", "benchmark"],
    "ai/nlp": ["ner", "nli", "sentiment", "tokenizer"],
}
for row in rows:
    text = f"{kategori} {hedef}".lower()
    for key, val in NE_RULES.items():
        if any(kw in text for kw in val):
            c.execute("UPDATE ogrenmeler SET ne=? WHERE id=?", (key, rid))
```

### 9b.6. Çıktı Formatı (Kullanıcının İstediği)

```
📊 5N1K — ANA BASLIKLAR ve ALT BASLIKLAR
NE (Konu/Kategori)
├── 🧩 ecc                 392
├── 🤖 AI                  160  (ML:160)
├── 🌐 Ağ                  137
├── 📏 degerlendirme        66
├── 📝 nlp                  49
├── 💬 prompt               51
```

**Tetikleyici:** Binlerce DB kaydını anlamlı kategorilere ayırma ihtiyacı.
**Pitfall:** "Diğer" etiketi %50'yi geçerse keyword listesi yetersizdir — genişlet.
**Pitfall:** Türkçe karakter (ı,ş,ü,ö) içeren kategoriler normalize edilmezse eşleşmez.
**Referans:** `.ReYMeN/memory_taxonomy_5n1k.md` — tam taksonomi dokümanı

---

## 10. Belirsiz Görev → Hafıza Tabanlı Öneri (İyileştirme 4)

Bir görev belirsiz olduğunda (örn. "sistemi güvenli yap") LLM'e gitmeden ÖNCE `oneri_uret()` fonksiyonu çağrılır.

```python
from reymen.hafiza.gorev_once_kontrol import oneri_uret
oneri = oneri_uret("sistemi güvenli yap")
```

**Nasıl çalışır:**
1. Kullanıcının metnindeki kelimeler **5 kategori ağacı** ile karşılaştırılır
2. Her tetiklenen kategori için `hafizada_ara()` ile hafıza sorgulanır
3. Puan = kelime_eşleşme × 0.3 + hafıza_guven × 0.7
4. En yüksek puanlı kategori seçilir, kullanıcıya öneri sunulur

**5 kategori ağacı:**
| Kategori | Tetikleyici Kelimeler |
|:---------|:----------------------|
| kali/network/nmap | güvenli, port, tarama, nmap, ağ, servis, pentest |
| kali/web | web, site, sql, xss, burp, güvenlik |
| dron | dron, drone, uçur, px4, uav, iha |
| cad | cad, solidworks, çizim, 3d, tasarım |
| windows | windows, ekran, mouse, klavye, otomasyon |

**Tetikleyici:** Belirsiz görev geldiğinde, hafızada direk eşleşme yoksa.

**Pitfall:** "Merhaba" selamlaşmaları yanlış kategorilenebilir — selamlaşma filtresi engeller.

**Pitfall:** Kategori ağacı statiktir. Yeni kategori eklenmek istenirse `oneri_uret()` içindeki `kategori_agaci` listesine eleman eklenir.

---

## Referanslar

- `references/hafiza-oncelikli-akis-pattern.md` — 5 katman pre-check + 7 sınıf error analysis detayı ve kod örneği
- `references/karar-dongusu-ornek.md` — decisions.md örnek kaydı
- `references/self-improvement-cycle.md` — 6 adımlı aktif kendini geliştirme döngüsü (Gözlem→Teşhis→Araştır→Karar→Test→Uygula)
- `references/yanit-format-ornekleri.md` — Cave Mode örnek cevaplar, Kiral38 canlı veri formatı
- `references/reymen-test-rewrite-pattern.md` — Hermes reference test'lerini ReYMeN native test'e çevirme
- `references/cron-no-agent-pattern.md` — Token-free cron job pattern (no_agent bash script, counter deseni, 7-gün backup örneği)
- `references/memory-management-pattern.md` — Memory consolidation: batch remove/replace/add, old_text matching, 12K→1.4K örneği
- `references/test-runner-cron-pattern.md` — 15-dakikada-bir test cron'u, `-p no:capture` pitfall'ı
