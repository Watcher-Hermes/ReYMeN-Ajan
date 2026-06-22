# ReYMeN Hata Çözüm Sözlüğü

**Kaynak:** 39 session boyunca karşılaşılan tüm hatalar
**Tarih:** 2026-06-20

## Import Hataları

| Hata | Sebep | Çözüm |
|------|-------|-------|
| `ModuleNotFoundError: No module named 'tools'` | Import path yanlış | `importlib.import_module(f'tools.{name}')` |
| `agent.tool_guardrails` vs root | Claude yanlış import yazdı | Root seviye import kullan: `from tool_guardrails import ToolGuardrails` |
| `agent/tool_executor.py` karışıklığı | Root'ta (281 satır) ve agent/ (1016) var | **Root'taki kullanılır**, agent/ ReYMeN core |
| `No module named 'filelock'` | Dashboard bağımlılığı | `pip install filelock` |

## Dispatcher Hataları

| # | Hata | Çözüm |
|---|------|-------|
| 1 | `calistir_tool(name=...)` → `module_name` olmalı | Parametre adını değiştir |
| 2 | `import_module(name)` → `tools.{name}` eksik | `f'tools.{name}'` prefix ekle |
| 3 | `context` parametresi kullanılmıyor | `timeout` ile değiştir |
| 4 | Import yolu `agent.tool_guardrails` | Root import'a çevir |
| 5 | Atıf import (module -> tool aynıysa) | Doğrudan `from ... import ...` kullan |

## ACP Hataları

| Hata | Çözüm |
|------|-------|
| `proc.communicate()` chunk'ları blokluyor | `readline()` döngüsü ile değiştir |
| JSON decode hatası retry yok | Retry handler ekle |
| Timeout/connection retry yok | Ayrı retry handler |
| ProgressTracker: referans kopya | `copy.deepcopy` kullan |
| ProgressTracker: class-level `_baslama` | Instance-level değişken |
| ProgressTracker: süre yanlış | Doğru datetime math |

## Test Hataları

| Hata | Çözüm |
|------|-------|
| Claude refactor: class→function | Testleri de güncelle veya geri al |
| display.py: ANSI escape terminal değil | `capsys` ile yakala veya force ANSI |
| Token redact: `sk-ABC...7890` | `API_KEY=[REDACTED]` formatı kullan |
| Token redact: büyük/küçük harf | Regex `re.IGNORECASE` ekle |
| Token redact: `...` regex kırıyor | Üç noktayı kaçır veya kaldır |

## Windows Spesifik

| Hata | Çözüm |
|------|-------|
| `error: no commands supplied` (main.py) | Argümansız REPL başlatma -- imported modül sys.argv kontrol ediyor |
| Web UI port 8080 dolu | Port değiştir veya kullanan programı bul |
| `reymen.bat` multiline Python | Ayrı .py dosyasına çıkar |
| Pagefile (WinError 1455) | Bilgisayarı yeniden başlat |

## Session Corruption (#15236)

**Belirti:** Tool çağrıları argümanları bozuk gönderiyor
**Çözüm:** Yeni session başlat (`/new`), bozuk session'da karmaşık işlem yapma
