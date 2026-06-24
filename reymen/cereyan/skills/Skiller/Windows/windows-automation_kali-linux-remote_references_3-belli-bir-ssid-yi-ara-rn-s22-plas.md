# 3. Belli bir SSID'yi ara (örn: S22 PLAS)
ssh kali "sudo iw dev wlan0 scan 2>&1 | grep -A10 'SSID: S22 PLAS\|SSID: S 22 PLAS'"