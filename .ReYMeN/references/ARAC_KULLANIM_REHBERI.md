# ReYMeN Araç Kullanım Rehberi

**Kaynak:** 39 session boyunca kullanılan araç desenleri
**Tarih:** 2026-06-20

## Test Komutları

| Amaç | Komut |
|------|-------|
| Tüm testler | `python -m pytest tests/ -q --tb=short 2>&1 | tail -5` |
| Belirli testler | `python -m pytest test_a.py test_b.py -v --tb=short` |
| Test sayısı (çalıştırmadan) | `python -m pytest test_a.py --collect-only -q 2>&1 | tail -5` |
| Gateway testleri | `python -m pytest test_gateway_quality.py -v --tb=short -p no:warnings` |
| Sansür testleri | `python -m pytest tests/test_agent_redact.py -v --tb=line 2>&1` |

## Import Doğrulama

```bash
python -c "from beyin import Beyin; print('Beyin OK')"
python -c "from motor import Motor; print('Motor OK')"
python -c "from agent.transports import listele; t=listele(); print(len(t), 'transport')"
python -c "from tool_registry import ToolRegistry; tr=ToolRegistry(); print(len(tr.liste()), 'tool')"
python -c "from session_db import SessionDB; db=SessionDB(); print('SQLite OK')"
```

## Git Komutları

| Amaç | Komut |
|------|-------|
| Değişen .py dosyaları | `git diff --stat 2>&1 | grep '.py ' | grep -v 'venv/'` |
| Status filtreli | `git status --short 2>&1 | grep -E '\.py |\.md |\.json ' | grep -v 'venv/'` |
| Sadece yeni dosyalar | `git status --short 2>&1 | grep '^??'` |

## Patch Kullanımı

```python
patch(mode='replace',
      path='dosya.py',
      old_string='eski_kod',
      new_string='yeni_kod')
```

- Çok satırlı stringlerle çalışır
- Eşsiz eşleşme gerektirir (unique match)
- replace_all=True ile tüm eşleşmeleri değiştir

## Screenshot

```python
# Python 3.14 (global) kullan
python_exe = r"C:\Users\marko\AppData\Local\Python\PythonCore-3.14-64\python.exe"
terminal(command=f'"{python_exe}" -c "from mss import mss; ..."')
```

## Notepad ile Kullanıcıya İçerik Gönderme

```bash
write_file(path='MASAUSTU/dosya.md', content='...')
terminal(command='notepad "MASAUSTU/dosya.md"', background=true)
```

## Session Arşivleme

```bash
# 1. Session log yaz
write_file(path=f'.ReYMeN/oturumlar/{kaynak}/{session_id}.md', content=...)

# 2. INDEX.md güncelle
patch(old_string='| # | Tarih', new_string='yeni_satir\n| # | Tarih')

# 3. Sayıları güncelle
patch(old_string='Toplam: X', new_string='Toplam: X+1')
```
