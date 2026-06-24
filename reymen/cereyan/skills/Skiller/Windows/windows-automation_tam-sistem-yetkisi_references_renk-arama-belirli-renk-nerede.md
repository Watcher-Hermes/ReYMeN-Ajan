# Renk arama — belirli renk nerede?
found = pyautogui.locateOnScreen(r"C:\Users\marko\Downloads\hedef.png",
                                  confidence=0.9)
if found:
    pyautogui.click(found)
```

---