## 3. Mouse / Klavye Otomasyonu

### Kurulum (bir kez)

```bash
pip install pyautogui pillow
```

### Mouse tıklama ve hareket

```python
import pyautogui
import time

pyautogui.FAILSAFE = True   # Sol üst köşeye mouse giderse dur (guvenlik)
pyautogui.PAUSE   = 0.3     # Her eylem arası bekleme (saniye)