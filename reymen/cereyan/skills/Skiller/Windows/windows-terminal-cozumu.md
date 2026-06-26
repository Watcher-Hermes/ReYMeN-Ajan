---
name: windows-terminal-cozumu
title: Windows Terminal Çözümü
description: Hermes terminal tool'u OneDrive veya MSYS deadlock nedeniyle bloke olduğunda alternatif çözüm
---

# Windows Terminal Çözümü

## Ne Zaman Kullanılır
- `pwd`, `echo` gibi basit komutlar bile timeout atıyorsa
- `[Command timed out after Ns]` hatası tüm terminal çağrılarında tekrarlıyorsa
- Dosya okuma/yazma araçları da çalışmıyorsa
- `execute_code` içindeki terminal() de çalışmıyorsa

## Kök Neden
Hermes her oturumda **tek bir `bash -l` (login shell)** başlatır ve tüm terminal komutları bu shell üzerinden çalışır. Eğer:
- Bu shell OneDrive yolu üzerinde takılı kalırsa (`find`, `ls`)
- MSYS/git-bash job control deadlock'a girerse (`set -m`)
- Windows Defender veya OneDrive sync dosya erişimini bloke ederse

→ **Tüm terminal araçları bloke olur.**

## Çözüm 1: execute_code + Python stdlib (ÖNCELİKLİ — Hızlı, Az Token)
Terminal çalışmadığında `execute_code` içinde **Python stdlib** kullan:

| İşlem | Yöntem | Hız |
|-------|--------|-----|
| Dosya tarama | `os.walk()` + `ast.parse()` | Anında |
| Test çalıştırma | `subprocess.run()` | Normal |
| Dosya yazma | `open(path, "w")` **DEĞİL** `write_file` | 0.1sn vs 180sn timeout |
| Kod analizi | `ast.walk()` ile fonksiyon/metot tespiti | Anında |

**ÖNEMLİ:** `write_file` tool'u OneDrive yollarında timeout atar. `execute_code` içinde Python'un
built-in `open()` fonksiyonu sorunsuz çalışır. Büyük dosyaları 50 satırda bölerek yaz.

```python
# İYİ: execute_code içinde open() kullan
with open("hedef_dosya.md", "w") as f:
    f.write("içerik")

# KÖTÜ: write_file kullanma (timeout riski)
```

Bu yöntem `delegate_task`'ten **çok daha hızlı ve ucuz** (saniyeler vs dakikalar).

## Çözüm 2: Sub-Agent (Hermes içi) — Son Çare
- Sub-agent **taze bir shell** alır (ana oturumdaki stuck shell'den bağımsız)
- Tüm komutları **&& ile zincirle** (tek shell oturumunda çok iş)
- Her çağrıyı **odaklı ve kısa** tut

```
İYİ: cd /path && cat file.py && python test.py -v   (tek && zinciri)
KÖTÜ: tek tek terminal çağrıları (her biri ayrı shell, riskli)
```

## Çözüm 3: Kullanıcı (Windows)
Hermes dışında, Windows'ta bash.exe'yi öldür:
```
taskkill /f /im bash.exe
```
Hermes yeni shell açar, terminal düzelir.

## Çözüm 3: Önleyici (Config)
Terminal blokesini önlemek için:
```yaml
terminal:
  backend: local
  shell_init_files: []
  home_mode: auto
```

## Doğrulama
- `delegate_task` içinde terminal çalışıyorsa → çözüm geçerli
- `pwd && echo ok` 5sn içinde dönüyorsa → shell canlı

## Pitfall
- Sub-agent çağrıları pahalı (dakikalar, çok token). Sadece acil durumlarda.
- Uzun vadeli çözüm: Projeyi OneDrive dışında tut.

## Alternatifler
Terminal tamamen bloke olduğunda `references/terminal-bloke-alternatifleri.md`'ye bak — execute_code + os.walk + ast.parse ile terminal olmadan çalışma.
