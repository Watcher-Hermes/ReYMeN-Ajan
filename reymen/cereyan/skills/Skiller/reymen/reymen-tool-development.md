---
name: reymen-tool-development
description: ReYMeN Agent tool development pattern — how to create, register, and integrate new tools into the ReYMeN motor system.
---

# ReYMeN Tool Development

## When to Use
Creating new tool modules for ReYMeN Agent, registering them in motor.py, or closing feature gaps with Hermes Agent.

## Tool Module Template

Every tool in `reymen/arac/` follows this pattern:

```python
# -*- coding: utf-8 -*-
"""
<tool_name>.py — <description>.

Kullanım:
    from reymen.arac.<tool_name> import <main_function>
"""

# 1. Imports (graceful degrade for optional deps)
try:
    from reymen.sistem.reymen_logging import get_logger
    log = get_logger("<tool_name>")
except Exception:
    import logging
    log = logging.getLogger("<tool_name>")

# 2. Core class/functions
class ToolName:
    def __init__(self):
        pass
    
    def islem(self, ...):
        pass

# 3. Motor integration — REQUIRED
def run(param1: str = "", param2: str = "") -> str:
    """Motor entegrasyonu. Must return str."""
    ...

# 4. Standalone test
if __name__ == "__main__":
    import sys
    print(run(...))
```

## Registration in motor.py

In `reymen/cereyan/motor.py` → `_plugin_moduller_yukle()`:
```python
# Add to the moduller list:
"reymen.arac.<tool_name>",
```

## Key Rules

1. **`run()` function is MANDATORY** — motor.py calls `run()` via importlib
2. **Always return str** — motor expects string output
3. **Use `log` not `print()`** — all logging goes through `reymen.sistem.reymen_logging`
4. **Graceful degrade** — optional deps wrapped in try/except
5. **`if __name__ == "__main__"`** — standalone test block required

## Pitfalls

- Tool file name must be unique in `reymen/arac/` — motor.py imports by module name
- Don't use `text=True` in subprocess.run for PowerShell — use `.decode("utf-8", errors="replace")` for Turkish chars
- `Path(__file__).parent.parent.parent` breaks in Windows docstrings due to `\U` unicode escape — use forward slashes in docstrings

## 5N1K Table (Required for Skills)

| Alan | Açıklama |
|:-----|:---------|
| Kim | ReYMeN Agent geliştirici |
| Ne | Yeni tool modülü oluşturma |
| Nerede | `reymen/arac/` dizini |
| Ne Zaman | Yeni yetenek gerektiğinde |
| Neden | Agent'in araç setini genişletmek |
| Nasıl | Template + motor.py kaydı + test |
