# ReYMeN Kod Desenleri

**Kaynak:** 39 session'da geliştirilen ve düzeltilen kod yapıları
**Tarih:** 2026-06-20

## 1. Tool Dispatch Pipeline

Üç katmanlı tool dağıtımı:

```
ToolRegistry.resolve(name)
    → {module, callable, aciklama}
    → ToolGuardrails.kontrolet(module)
        → {guvenli: bool, sebep: str}
        → if callable == 'run':
            ToolExecutor.calistir_tool()
          else:
            _execute_function()
    → {'ok': bool, 'tool': str, ...}
```

## 2. Bridge Import (Çift Modül Koruma)

İki dosyada aynı sınıf varsa (root/ + agent/):

```python
# agent/tool_guardrails.py
from tool_guardrails import *  # Kök sürümü kullan
from tool_guardrails import ToolGuardrails
```

## 3. Dinamik Import

```python
import importlib
modul = importlib.import_module(f'tools.{module_adi}')  # tools/ prefix OLMALI
fonksiyon = getattr(modul, fonksiyon_adi)
```

## 4. Güvenli Fonksiyon Çağrısı

```python
sonuc = executor.calistir_guvenli(fn, timeout=timeout, **args)
# timeout + retry korumalı
```

## 5. Test Mock Desenleri

```python
# restart() mock
mock_os_execv = mocker.patch('os.execv')
mock_sys_exit = mocker.patch('sys.exit')

# menu() mock
mocker.patch('builtins.input', side_effect=EOFError())

# onay_iste() mock - EVET
mocker.patch('ctypes.windll.user32.MessageBoxW', return_value=6)  # 6=EVET

# onay_iste() mock - HAYIR
mocker.patch('ctypes.windll.user32.MessageBoxW', return_value=7)  # 7=HAYIR
```

## 6. Test Dosyası Şablonu

```python
# -*- coding: utf-8 -*-
"""test_modul.py — Modül adı için testler"""
import pytest
from unittest.mock import MagicMock, patch

class TestModul:
    def test_basarili(self):
        assert True

    def test_hata_durumu(self):
        with pytest.raises(ValueError):
            raise ValueError("test")
```

## 7. Provider Mock (Harici Servisler İçin)

```python
@pytest.fixture
def mock_provider():
    provider = MagicMock()
    provider.sorgula.return_value = {"sonuc": "test"}
    return provider
```

## 8. Dispatcher Timeout Kullanımı

```python
class ToolDispatcher:
    def __init__(self, varsayilan_timeout: int = 30):
        self.varsayilan_timeout = varsayilan_timeout

    def dispatch(self, tool, timeout=None):
        timeout = timeout or self.varsayilan_timeout
        ...
```
