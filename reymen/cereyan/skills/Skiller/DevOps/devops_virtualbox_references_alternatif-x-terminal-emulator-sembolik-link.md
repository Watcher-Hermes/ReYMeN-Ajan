# Alternatif: x-terminal-emulator (sembolik link)
MSYS2_ARG_CONV_EXCL="*" "C:\Program Files\Oracle\VirtualBox\VBoxManage.exe" \
  guestcontrol "kal" start --exe "/usr/bin/x-terminal-emulator" --username kali --password kali
```

**Örnek 2 — Kali'de komut çalıştır ve çıktıyı al:**

```bash
MSYS2_ARG_CONV_EXCL="*" "C:\Program Files\Oracle\VirtualBox\VBoxManage.exe" \
  guestcontrol "kal" run --exe "/usr/bin/whoami" --username kali --password kali --wait-stdout