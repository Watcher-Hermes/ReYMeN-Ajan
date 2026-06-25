# Nmap UDP Tarama Referansı

Session: 2026-06-21 — Kali nmap UDP taraması, localhost (127.0.0.1)

## Komut
```bash
nmap -sU -T4 127.0.0.1
```

## Çıktı
```
Nmap 7.80
PORT    STATE         SERVICE
137/udp open|filtered netbios-ns
1900/udp open|filtered upnp
4500/udp open|filtered nat-t-ike
5050/udp open|filtered mmcc
5353/udp open|filtered zeroconf
5355/udp open|filtered llmnr
```

## TCP Karşılaştırması
```
PORT    STATE  SERVICE     VERSION
135/tcp open   msrpc       Microsoft Windows RPC
445/tcp open   microsoft-ds Microsoft Windows SMB
1234/tcp open  http        Node.js Express framework
```

## Öğrenilenler
- `-sU`: UDP port taraması (TCP'den ~4x yavaş)
- UDP'de "open|filtered" normaldir: paket kaybı yoksa net bilgi alınamaz
- En yaygın UDP portları: 53(DNS), 67/68(DHCP), 137/138(NetBIOS), 161(SNMP), 5353(mDNS)
- Hız için `-T4` veya `--min-rate` kullanılabilir
- UDP taraması root yetkisi gerektirmez

## Hafıza Güncelleme
Bilgi mevcut DB kaydına (id=1972) güncellendi — yeni kayıt açılmadı:
- flag_udp: True
- acik_udp_port: 6
- kullanim_sayisi: 2 → 3
