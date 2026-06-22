# 1. Önce managed moda geç
ssh kali "sudo iw dev wlan0 set type managed && sudo ip link set wlan0 up && sleep 1"