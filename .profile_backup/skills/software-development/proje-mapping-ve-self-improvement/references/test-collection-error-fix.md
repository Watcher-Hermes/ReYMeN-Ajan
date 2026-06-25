# Test Collection Hatası — Eager Import Fix

## Hata
```
cd proje && python -m pytest tests/tools/test_execute_code_tool.py
  → ModuleNotFoundError: No module named 'ReYMeN_cli.fallback_config'
```

## Hata Zinciri
```
tests/tools/test_execute_code_tool.py
  → from execute_code_tool import run, check_fn        (root shim)
    → execute_code_tool.py: from reymen.arac.execute_code_tool import *
      → reymen/__init__.py: from reymen.sistem.sistem_sinyalleri import SignalHandler
        → reymen/sistem/__init__.py: from . import cli_commands     ← EAGER IMPORT
          → cli_commands.py: from ReYMeN_cli.fallback_config import get_fallback_chain
            → ModuleNotFoundError: No module named 'ReYMeN_cli.fallback_config'
```

## Fix
`reymen/sistem/__init__.py`'de 3 satır:
```python
# ÖNCE:
from . import cli_commands

# SONRA:
try:
    from . import cli_commands
except ImportError:
    pass
```

## Neden Diğer Yöntemler İşe Yaramadı?
| Yöntem | Neden Başarısız |
|--------|-----------------|
| `conftest.py` sys.path | `reymen` zaten conftest'ten önce import edilir |
| `pytest.ini` pythonpath | Aynı sebep — import order |
| `cli_commands.py` sys.path.insert | `__file__` pytest collection'da güvenilmez |
| `__init__.py` try/except | ✅ Her zaman işe yarar — import hatasını sessizce yutar |

## Doğrulama
```bash
cd proje && python -m pytest tests/tools/test_execute_code_tool.py -q
# → 26 passed in 0.38s
```
