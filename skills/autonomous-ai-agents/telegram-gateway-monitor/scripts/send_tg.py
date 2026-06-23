import json, urllib.request, urllib.parse, os, sys

# Profil parametresi al veya varsayılan kullan
profile = sys.argv[1] if len(sys.argv) > 1 else 'kiral38'
env_path = os.path.join(r'C:\Users\marko\AppData\Local\hermes\profiles', profile, '.env')

target_chat = sys.argv[2] if len(sys.argv) > 2 else '6328823909'

with open(env_path) as f:
    for line in f:
        line = line.strip()
        if line.startswith('TELEGRAM_BOT_TOKEN='):
            token = line.split('=', 1)[1]
            break

data = urllib.parse.urlencode({
    'chat_id': target_chat,
    'text': f'ReYMeN test - API dogrudan calisiyor (profil: {profile})'
}).encode()

r = urllib.request.urlopen(f'https://api.telegram.org/bot{token}/sendMessage', data=data)
result = json.loads(r.read())
print(f'Profil: {profile}, Hedef: {target_chat}')
print(json.dumps(result, indent=2))
