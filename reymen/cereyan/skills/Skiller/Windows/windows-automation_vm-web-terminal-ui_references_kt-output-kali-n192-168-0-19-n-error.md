# Çıktı: {"output": "kali\n192.168.0.19\n", "error": ""}
```

**Kritik:** Kali'de default shell **zsh**. Çok satırlı komutlar ve tırnak içinde `$()` kullanımı hata verir. Komutları tek satırda `&&` ile birleştir, tek tırnak kullan:

```