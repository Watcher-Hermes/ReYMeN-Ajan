# motor/ — Modüler Motor Paketi

`reymen/cereyan/motor.py` (2,048 satır) → `motor/` (6 dosya, 1,730 satır)

## Dosyalar

| Dosya | Satır | Sorumluluk |
|:------|:-----:|:-----------|
| `__init__.py` | 13 | Public API export (Motor, provider_degistir, CORE_TOOLS) |
| `config.py` | 176 | Sabitler, regex, toolset grupları, provider map |
| `context.py` | 80 | Context compression, prompt caching, PII temizlik, gateway state |
| `providers.py` | 124 | Provider yönetimi (setup.json, test, değiştirme) |
| `plugins.py` | 163 | ToolRegistry, PluginManager, lazy batch, skill/hook araçları |
| `main.py` | 1,174 | Motor class (eylem çözümleme, araç yönlendirme, fallback) |

## Kullanım (değişmedi)

```python
from reymen.cereyan.motor import Motor

m = Motor()
m.calistir("DOSYA_OKU", '"test.txt"')
```

## Bağımlılık Zinciri

```
config.py           ← hiçbir modüle bağımlı değil
context.py          ← config
providers.py        ← config
plugins.py          ← config
main.py             ← config + context + providers + plugins
```

## Gelecek İyileştirmeler

- `main.py` (1,174 satır) ikinci sprint'te bölünebilir
  - `_fallback_calistir` (550 satır) → `fallback.py`
  - Telegram araçları → `telegram.py`
  - Gateway araçları → `gateway.py`
