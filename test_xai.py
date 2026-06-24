import os, json, urllib.request

with open(os.path.expanduser("~/AppData/Local/hermes/profiles/reymen/.env")) as f:
    for line in f:
        if "XAI_API_KEY" in line:
            key = line.strip().split("=", 1)[1]
            break

data = json.dumps({"model": "grok-3-mini", "messages": [{"role": "user", "content": "Merhaba, test."}], "max_tokens": 10}).encode()
req = urllib.request.Request("https://api.x.ai/v1/chat/completions", data=data, headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
try:
    resp = urllib.request.urlopen(req, timeout=15)
    print(resp.read().decode()[:300])
except Exception as e:
    print(f"Hata: {e}")
