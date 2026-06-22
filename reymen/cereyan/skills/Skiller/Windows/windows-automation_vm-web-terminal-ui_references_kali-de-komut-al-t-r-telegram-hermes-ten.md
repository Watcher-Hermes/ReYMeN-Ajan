# Kali'de komut çalıştır — Telegram Hermes'ten
import urllib.request, json
data = json.dumps({"cmd": "whoami && hostname -I"}).encode()
req = urllib.request.Request("http://localhost:5050/exec", data=data, headers={"Content-Type": "application/json"})
resp = urllib.request.urlopen(req, timeout=30)
print(resp.read().decode())