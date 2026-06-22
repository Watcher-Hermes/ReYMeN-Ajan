# Yönetici PowerShell'de (Ctrl+Shift+Enter)
netsh wlan show networks mode=bssid
```

**Yönetici PowerShell açma:**
```bash
powershell.exe -NoProfile -Command "Start-Process powershell -Verb RunAs -ArgumentList '-NoProfile -Command \"netsh wlan show networks mode=bssid; pause\"'"
```