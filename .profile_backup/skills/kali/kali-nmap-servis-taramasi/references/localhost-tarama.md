# Kali Nmap — Localhost Tarama Referansı

Gerçek çıktı: `nmap -sV -T4 127.0.0.1` (Nmap 7.80, Windows 10)

## Açık Portlar (TCP)

```
PORT    STATE  SERVICE         VERSION
135/tcp open   msrpc           Microsoft Windows RPC
445/tcp open   microsoft-ds    Microsoft Windows SMB
1234/tcp open  http            Node.js Express framework
```

## Açık Portlar (UDP)

```
PORT    STATE         SERVICE
137/udp open|filtered netbios-ns
1900/udp open|filtered upnp
4500/udp open|filtered nat-t-ike
5050/udp open|filtered mmcc
5353/udp open|filtered zeroconf
5355/udp open|filtered llmnr
```

## Kullanılan Flag'ler

| Flag | Açıklama | Ne Zaman |
|:-----|:---------|:---------|
| `-sV` | Servis/versiyon tespiti | Default |
| `-sU` | UDP taraması | UDP portları için |
| `-T4` | Hızlı mod | Normal (T3 varsayılan, T4 hızlı) |

## Gözlemler

- **UDP** taraması TCP'den ~4x daha yavaş (29sn vs 7sn)
- **UDP'de "open|filtered"** normaldir — paket kaybı yoksa net ayrım yapılamaz
- **localhost'ta** host discovery (ping) otomatik atlanır
- **Docker** (kubernetes.docker.internal) hostname olarak görünür
