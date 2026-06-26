# MIGRATION.md — motor.py Geçiş Kılavuzu

## Eski → Yeni Import Rehberi

| Eski (motor.py) | Yeni (motor/) |
|:----------------|:--------------|
| `from reymen.cereyan.motor import Motor` | **Değişmedi** (shim üzerinden) |
| `from reymen.cereyan.motor import CORE_TOOLS` | **Değişmedi** (__init__ export) |
| `from reymen.cereyan.motor import get_active_tools` | **Değişmedi** |
| `from reymen.cereyan.motor import provider_degistir` | **Değişmedi** |
| `motor._REGISTRY` | `from reymen.cereyan.motor.plugins import _REGISTRY` |

## Breaking Changes
**YOK** — Tüm public API korundu.

## Deprecation
`motor.py` (shim) kalıcıdır — eski import'lar sonsuza kadar çalışır.

## Yeni Dosyalara Direkt Erişim

```python
# Gerekirse direkt import (shim'i atlar)
from reymen.cereyan.motor.config import TOOLSET_GRUPLARI, DURUM_MESAJLARI
from reymen.cereyan.motor.providers import setup_oku, provider_test_et
from reymen.cereyan.motor.plugins import lazy_module_listesi
from reymen.cereyan.motor.context import cevabi_temizle, gateway_durum_yaz
```

## Yedek
Eski motor.py (2,048 satır): `motor.py.bak.2048`
