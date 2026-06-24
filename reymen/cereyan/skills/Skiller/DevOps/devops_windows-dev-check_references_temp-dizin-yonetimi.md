# KIRILMA KOŞULU 5 — Temp Dizin Yönetimi

**Tetikleyici:** `tempfile.TemporaryDirectory`

**Kırılma:** Context manager çıkarken içindeki read-only dosyayı silemez → PermissionError

**Çözüm:**
```python
import tempfile, shutil
tmp = tempfile.mkdtemp()  # TemporaryDirectory YERINE
try:
    yield tmp
finally:
    shutil.rmtree(tmp, ignore_errors=True)  # manuel cleanup
```
