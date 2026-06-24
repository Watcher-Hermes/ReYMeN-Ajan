## Mimari

```
Windows Host (Hermes)
  └─ Flask server (localhost:5050)
       └─ Paramiko SSH client
            └─ Kali VM (192.168.0.19:22 - bridged)
                 └─ shell / tmux
```

- Flask, Windows'ta Python ile çalışır
- Paramiko ile Kali'ye SSH bağlanır
- Web arayüzü: HTML + CSS (dark tema) + JavaScript (fetch API)
- Masaüstü kısayolu (.bat) ile tek tıkla başlatılır