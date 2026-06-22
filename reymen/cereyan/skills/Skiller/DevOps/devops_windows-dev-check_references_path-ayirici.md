# KIRILMA KOŞULU 7 — Evrensel Path Ayırıcı

**Tetikleyici:** Sabit `\` veya `/` içeren dosya yolu

**Kırılma:** Windows `\` kullanır, Linux `/` kullanır. Sabit ayırıcı çapraz platformda kırılır.

**Çözüm:**
```python
from pathlib import Path
yol = Path("skills") / "alt_dizin" / "dosya.md"

# veya
import os
yol = os.path.join("skills", "alt_dizin", "dosya.md")
```
