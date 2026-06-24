# ReYMeN Windows Bilgi Bankası

**Kaynak:** 39 session, 1.982 mesaj işlenerek oluşturuldu
**Tarih:** 2026-06-20

## Komut Farklılıkları

| Windows | Linux/Mac | Açıklama |
|---------|-----------|----------|
| `python` | `python3` | Windows'ta `python3` diye komut YOK |
| `C:\Users\marko\...` | `/home/user/...` | Yol formatı farkı |
| `notepad` | `nano/vim` | Metin düzenleyici |
| `tasklist` | `ps aux` | Process listeleme |
| `find` | `grep` | Alternatif: `findstr` |

## Python Sürümleri

| Sürüm | Yol | Kullanım |
|-------|-----|----------|
| 3.11.15 | ReYMeN venv | Ana geliştirme ortamı |
| 3.14 | Global | Screenshot (mss + Pillow) |

## Sık Karşılaşılan Hatalar

### WinError 1455 — Sayfa dosyası çok küçük
- **Belirti:** terminal() hata kodu 3221225773, `echo test` bile çalışmaz
- **Çözüm:** Bilgisayarı yeniden başlat veya sayfa dosyasını büyüt
- **Etki:** Tüm terminal/test işlemleri bloke olur

### PIL ImportError
- **Belirti:** `from PIL import Image` → `cannot import name '_imaging'`
- **Sebep:** Venv Python 3.11 iken Pillow 3.14 için derlenmiş
- **Çözüm:** Doğru Python sürümüyle eşleşen Pillow kullan

### Batch multiline Python
- **Belirti:** `.bat` içinde `python -c "..."` çok satırlı kod çalışmaz
- **Sebep:** Windows batch her satırı ayrı komut sayar
- **Çözüm:** Python kodunu ayrı `.py` dosyasına çıkar

### .env bulunamadı
- **Belirti:** `reymen start` → `.env` hatası
- **Sebep:** Script CWD'den arar, proje kökünde değilse bulamaz
- **Çözüm:** Mutlak yol kullan veya proje dizininden çalıştır

## Tesseract OCR

| Özellik | Değer |
|---------|-------|
| Yol | `C:\Program Files\Tesseract-OCR\tesseract.exe` |
| PSM 4 | Tek sütunlu listeler için |
| PSM 6 | Metin blokları için |
| Limit | Çıktı ~3000 karakterle sınırla |
| Karanlık tema | `ImageOps.invert()` veya parlaklık artır |

## VS Code Kontrol

- `type_in_vscode.py` ile metin yazma
- Klavye kısayolları: ctrl+s, ctrl+z
- Dosya açma: VS Code API
