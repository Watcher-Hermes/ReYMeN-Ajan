# Özel tuşlar
pyautogui.press(["left", "left", "right"])
pyautogui.keyDown("shift")
pyautogui.press("end")
pyautogui.keyUp("shift")
```

### Belirli bir pencereye odaklanma (Windows)

```python
import subprocess, time, pyautogui