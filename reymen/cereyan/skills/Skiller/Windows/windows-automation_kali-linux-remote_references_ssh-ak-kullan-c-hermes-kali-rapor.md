## SSH Akışı (Kullanıcı → Hermes → Kali → Rapor)

```
Kullanıcı → komutu yazar (örn: "sudo arp-scan -l")
    ↓
Hermes → terminal tool ile SSH yapar: ssh kali "<komut>"
    ↓
Kali → komutu çalıştırır, çıktı SSH üzerinden döner
    ↓
Hermes → kendi terminalinde çıktıyı alır
    ↓
Hermes → kullanıcıya sonucu raporlar (sadece çıktı, yorum yok)
```

**Akış kuralları:**
- Hermes kendi terminalinde sonucu görür → kullanıcıya raporlar
- Yorum yapma, adım adım açıklama yok — sadece çıktı
- "Sorma sonucun raporla bitti" modu