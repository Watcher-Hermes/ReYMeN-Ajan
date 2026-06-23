import json, sys, os

# Profil parametresi al veya varsayılan kullan
profile = sys.argv[1] if len(sys.argv) > 1 else 'reymen'
profiles_root = r'C:\Users\marko\AppData\Local\hermes\profiles'
path = os.path.join(profiles_root, profile, 'gateway_state.json')

state = {
    'pid': None,
    'kind': f'{profile}-gateway',
    'gateway_state': 'stopped',
    'platforms': {
        'telegram': {
            'state': 'disconnected',
            'error_code': None,
            'error_message': None
        }
    }
}

with open(path, 'w') as f:
    json.dump(state, f)

print(f'Gateway state reset OK for profile: {profile}')
print(f'Path: {path}')
print(f'State: {json.dumps(state)}')
