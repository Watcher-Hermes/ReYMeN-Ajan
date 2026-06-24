# ÇALIŞMAZ — sadece root ile
adb shell "pm set-debug com.target.package true"
```

**4. Uygulama etkinliğini kontrol et:**
```bash
adb shell "dumpsys package com.target.package | grep enabled"