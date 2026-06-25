---
name: cross-platform-coordination
description: Çoklu ajan koordinasyon desenleri — Kali+Windows güvenlik iş akışları, mesaj formatı, hata yönetimi, hafıza paylaşımı
category: cross-platform
version: 1.0.0
triggers:
  - koordinasyon
  - multi-agent
  - ajan konusma
  - kali windows
  - port engelleme
  - orchestrator
  - coordinator
  - cross-platform
---

# Cross-Platform Koordinasyon

İki veya daha fazla ajanın (Kali, Windows, vs.) koordineli çalışması için desenler.

## Kanonik Örnek: Port Engelleme

```
┌─────────┐    BLOCK_PORT(4444)    ┌──────────┐    PORT_BLOCKED(engellendi)    ┌─────────┐
│  Kali   │ ─────────────────────→ │ Windows  │ ──────────────────────────────→ │  Kali   │
│ (tespit)│ ←─────────────────────│(engelle) │ ←──────────────────────────────│ (onay)  │
└─────────┘      doğrula(4444)      └──────────┘      yeniden tara(4444)       └─────────┘
```

### Koordinasyon Adımları

| # | Ajan | Rol | Eylem | Hafıza Kategorisi |
|:-:|:----:|:---:|:------|:-----------------:|
| 1 | Kali | **Orkestratör** (tespit eden) | `nmap -sV -p 1-65535 localhost` → şüpheli port bul | `kali/network/nmap` |
| 2 | Kali | Orkestratör | `{cmd: BLOCK_PORT, port, protocol, kaynak}` → Windows'a gönder | — |
| 3 | Windows | **Çalışan** (engelleyen) | `netstat -an` ile doğrula → firewall kuralı ekle | `windows/terminal/network` |
| 4 | Windows | Çalışan | `{cmd: PORT_BLOCKED, port, durum, kaynak, rule_name}` → Kali'ye bildir | — |
| 5 | Kali | **Doğrulayıcı** (onay alan) | `nmap -p <port> localhost` → `filtered` görmeli | `cross-platform/security` |

## Mesaj Formatı

JSON-RPC benzeri, 4 alan zorunlu:

| Alan | Tip | Örnek |
|:-----|:----|:------|
| `cmd` | string | `BLOCK_PORT`, `PORT_BLOCKED` |
| `port` | int | `4444` |
| `protocol` | string | `tcp`, `udp` |
| `kaynak` | string | `kali`, `windows` |
| `durum` | string (ops) | `engellendi`, `hata`, `beklemede` |
| `rule_name` | string (ops) | `BLOCK_SUSPICIOUS_4444` |

**Kali → Windows:**
```json
{"cmd": "BLOCK_PORT", "port": 4444, "protocol": "tcp", "kaynak": "kali", "severity": "high"}
```

**Windows → Kali:**
```json
{"cmd": "PORT_BLOCKED", "port": 4444, "durum": "engellendi", "kaynak": "windows", "rule_name": "BLOCK_SUSPICIOUS_4444"}
```

## Ajan Rolleri

| Rol | Görev | Sahibi |
|:----|:------|:-------|
| **Orkestratör** | Tespit eder, görevi başlatır, bitince onaylar | Kali (tespit aracı) |
| **Çalışan** | Fiziksel eylemi gerçekleştirir (firewall, servis durdurma) | Windows (hedef sistem) |
| **Doğrulayıcı** | Eylemi doğrular, kapatır | Kali (harici tarama) |

Orkestratör = her zaman **tespit eden** ajandır.

## Hata Yönetimi

| Hata | Etki | Düzeltici |
|:-----|:-----|:----------|
| Kali nmap hatası | Port tespit edilemez | Windows tek başına tarama yapamaz — Kali yeniden dene |
| Windows firewall hatası | Kural eklenemez | Kali elle engelleme talimatı döndürür |
| İletişim kopması | Mesaj kaybolur | Her iki ajan da 30sn bekle → maximum 3 retry |
| Port zaten engelli | Çakışma | `netsh advfirewall firewall show rule` ile kontrol et → atla |

## Hafıza Paylaşımı

- **Depo:** Ortak `hafiza.db` (tek dosya, ayrı kategoriler)
- **Kategoriler:**
  - `kali/network/nmap` — Kali nmap sonuçları
  - `windows/terminal/network` — Windows ağ komutları
  - `cross-platform/security` — Koordinasyon kayıtları
- **Guven_skoru:** `_kademeli_guven()` sigmoid ile hesaplanır: `1/(1+e^(-0.5*(basari-hata-1)))`. İlk kayıt 0.5 başlar, 10 başarıda ~0.99 olur. (Detay: `web-dogrulama-dongusu` skill'i → `references/kademeli-guven-kaydet-api.md`)
- **Guven_skoru eşiği:** ≥ 0.8 → LLM atlanır, hafızadan direkt döner
- **Yeni kayıt formatı:**
  ```json
  {
    "koleksiyon": "beceriler",
    "kategori": "cross-platform/security",
    "guven_skoru": 1.0,
    "gecerlilik_tarihi": "<bugun+6ay>"
  }
  ```

## ReYMeN Inter-Agent v1 Protokolü

Bu skill'in altında geliştirilen zengin protokol. Hafızada `cross-platform/security` kategorisinde saklanır.

```
from:     <ajan_adi>        # kali_agent veya windows_agent
to:       <hedef_ajan>      # windows_agent veya kali_agent
protocol: ReYMEN_InterAgent_v1
payload:
  type:       security_alert | command | status
  severity:   low | medium | high | critical
  ports:      [port_no, ...]
  action:     verify_and_block | block_only | check_only
  confidence: 0.0 - 1.0
```

## LLM Maliyeti

| Adım | LLM çağrısı | Süre | Maliyet |
|:-----|:-----------:|:----:|:-------:|
| Kali nmap hafıza sorgusu | 0 (guven=1.0 > 0.8) | 9.18sn | 0₺ |
| nmap çalıştırma (tool) | 0 (tool) | — | 0₺ |
| Windows netstat hafıza sorgusu | 0 (guven=1.0 > 0.8) | ~0.1sn | 0₺ |
| netstat çalıştırma (tool) | 0 (tool) | 0.5sn | 0₺ |
| **TOPLAM** | **0 çağrı** | **~10sn** | **0₺** |

Kanıtlanmış: 4 adımlık koordinasyon → **0 LLM çağrısı** (tümü hafıza atlaması). Sadece hafıza miss + yeni senaryo: **1 LLM çağrısı**.

## Öğrenme Kaydı Formatı (Hafıza)

```json
{
  "koleksiyon": "beceriler",
  "anahtar": "kali windows port engelleme koordinasyonu",
  "icerik": "# ✅ Başarılı: ... \n## Süreç:\n1. ...",
  "metadata": {
    "guven_skoru": 1.0,
    "kategori": "cross-platform/security",
    "gecerlilik_tarihi": "<bugun+6ay>",
    "kullanim_sayisi": 1
  }
}
```

- Aynı `anahtar` + `kategori` → `kaydet()` UPDATE yapar (yeni kayıt açmaz)
- `guven_skoru` ≥ 0.8 → `once_hafiza.ara()` LLM atlar, direkt döner

## Simülasyon Script'i

`scripts/simulate_coordination.py` — Python ile tüm akışı baştan sona çalıştırır:
- `once_hafiza()` ile 3 hafıza sorgusu (Kali nmap, Windows netstat, Windows firewall)
- `hafiza_kaydet()` ile 3 yeni kayıt ekler (firewall, koordinasyon, doğrulama)
- LLM sayacı + süre + maliyet raporu verir

Çalıştırmak için: `skill_view('cross-platform-coordination', 'scripts/simulate_coordination.py')` içeriğini al → terminal ile çalıştır.

## Referanslar

- `references/coordination-simulation.md` — Simülasyon detayları
- `scripts/simulate_coordination.py` — Çalıştırılabilir simülasyon script'i

## Pitfalls

- Hafızada aynı kategori altında farklı anahtarlar olabilir — `once_hafiza.ara()` en güncelini döndürür
- Mesaj formatı JSON değil, JSON-benzeri metin — `json.loads()` yerine regex veya string parse et
- `nmap filtered` port iletimi engellendiği anlamına gelir, port kapalı değil — firewall çalışıyor demek
- Windows'ta netsh komutları **yönetici yetkisi** gerektirir — terminal yönetici değilse hata alınır
