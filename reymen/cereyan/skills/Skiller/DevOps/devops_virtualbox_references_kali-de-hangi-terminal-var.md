# Kali'de hangi terminal var?
MSYS2_ARG_CONV_EXCL="*" "C:\Program Files\Oracle\VirtualBox\VBoxManage.exe" \
  guestcontrol "kal" run --exe "/usr/bin/ls" --username kali --password kali \
  --wait-stdout -- -la /usr/bin/ | grep -i term