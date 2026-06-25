---
name: kali-nmap-servis-taramasi
description: Kali Linux Nmap ile servis versiyon tespiti — OnceHafiza entegre
category: kali
version: 1.0.0
triggers:
  - nmap
  - port tarama
  - servis tespiti
  - versiyon tespiti
---

# Kali Nmap Servis Versiyon Tespiti

## Hedef
Hedef sistemdeki açık portları ve çalışan servis versiyonlarını tespit et.

## Kullanım
```bash
nmap -sV -T4 <hedef_ip>
```

| Flag | Açıklama |
|:-----|:---------|
| `-sV` | Servis/versiyon tespiti (Service/Version Detection) |
| `-T4` | Hızlı tarama (Timing template 4) |
| `-p <port>` | Belirli portları tara (örn. `-p 22,80,443`) |
| `--version-intensity <0-9>` | Versiyon tespit yoğunluğu (0=hafif, 9=tüm problar) |
| `-sU` | UDP taraması (TCP'den ~4x yavaş) |
| `-O` | OS tespiti (isteğe bağlı) |

## Örnek Çıktı (TCP)
```
PORT     STATE  SERVICE         VERSION
135/tcp  open   msrpc           Microsoft Windows RPC
445/tcp  open   microsoft-ds    Microsoft Windows SMB
1234/tcp open   http            Node.js Express framework
```

## Örnek Çıktı (UDP)
```
PORT    STATE         SERVICE
137/udp open|filtered netbios-ns
1900/udp open|filtered upnp
5353/udp open|filtered zeroconf
5355/udp open|filtered llmnr
Not: UDP'de "open|filtered" normaldir - paket kaybı yoksa net bilgi alınamaz
```

## OnceHafiza Kullanımı
```python
from once_hafiza import isle, hafizada_ara

# Hafızaya bak, yoksa çalıştır
sonuc = isle(
    "nmap ile port tara 127.0.0.1",
    lambda: terminal("nmap -sV -T4 127.0.0.1"),
    kategori="kali/network/nmap",
)

# Sorgula
kayit = hafizada_ara("servis versiyon tespiti", kategori="kali/network/nmap")
if kayit["bulundu"] and kayit["guven_seviyesi"] != "belirsiz":
    print(f"Guvenilir kayit: {kayit['icerik'][:100]}")
```

## Metadata
- `guven_skoru`: 0.6 (başlangıç), 1.0'a kadar yükselir
- `gecerlilik_tarihi`: +180 gün
- `kategori`: kali/network/nmap

## Referanslar
- `references/localhost-tarama.md` — Gerçek nmap çıktısı (TCP + UDP), flag'ler, gözlemler

## Pitfall'lar
- **Yetki**: `-sV` bazen root yetkisi ister, değilse `-sT` (TCP Connect) dene
- **Hız**: Tüm 65535 port taranacaksa `-p-` ekle, ama çok yavaşlar
- **Güvenlik Duvarı**: Hedefte firewall varsa `-Pn` ekle (host discovery atla)
- **Yerel**: localhost'ta `-sV` her zaman çalışır, host discovery gerekmez
- **UDP yavaşlığı**: `-sU` TCP'den ~4x yavaştır. `-T4` veya `--min-rate` ile hızlandır

## Referanslar
- `references/udp-tarama-ornek-cikti.md` — UDP taraması örnek çıktı ve öğrenilenler
- **Kayıt güncelleme**: TCP taraması + UDP taraması ayrı KAYITLAR değil, aynı kaydın genişlemesidir. `gorev_sonrasi_hafiza()` ile yeni kayıt açma, `hafiza.kayit_guncelle()` ile mevcut kaydın içeriğine UDP bilgisini EKLE. Detay: `reymen-kontrol-kurali` Kural 6a.
